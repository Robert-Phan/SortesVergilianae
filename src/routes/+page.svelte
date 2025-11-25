<script lang="ts">
	import type { PageProps } from './$types';
	import type { Verse } from '../../resources/load_verses';
    import { onMount } from 'svelte';

	let { data }: PageProps = $props();

	// State for user selections
	let language = $state<'latin' | 'english'>('latin');
	let selectedBooks = $state<number[]>([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    $inspect(selectedBooks)
	let lineCount = $state(5);
	
	// State for results
	let selectedVerse = $state<Verse | null>(null);
	let linesAbove = $state<string[]>([]);
	let linesBelow = $state<string[]>([]);
	let peekAboveCount = $state(3);
	let peekBelowCount = $state(3);
	let startLineNumber = $state(0);
	let endLineNumber = $state(0);

	// Available books (1-12 for the Aeneid)
	const availableBooks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

	// Toggle book selection
	function toggleBook(book: number) {
		if (selectedBooks.includes(book)) {
			selectedBooks = selectedBooks.filter((b) => b !== book);
		} else {
			selectedBooks = [...selectedBooks, book].sort((a, b) => a - b);
		}
	}

	// Toggle all books
	function toggleAllBooks() {
		if (selectedBooks.length === availableBooks.length) {
			selectedBooks = [];
		} else {
			selectedBooks = [...availableBooks];
		}
	}

	// Get all lines from all verses in order
	function getAllLines(): { line: string; lineNumber?: number; book: number; verse: Verse }[] {
		const verses = language === 'latin' ? data.latin : data.english;
		const result: { line: string; lineNumber?: number; book: number; verse: Verse }[] = [];
		
		if (language === 'latin') {
			for (const verse of verses) {
				let currentLineNumber = verse.line_numbers[0];
				for (const paragraph of verse.paragraphs) {
					for (const line of paragraph) {
						result.push({ line, lineNumber: currentLineNumber, book: verse.book, verse });
						currentLineNumber++;
					}
				}
			}
		} else {
			for (const verse of verses) {
				for (const paragraph of verse.paragraphs) {
					for (const line of paragraph) {
						result.push({ line, book: verse.book, verse });
					}
				}
			}
		}
		
		return result;
	}

	// Pick random verses
	function pickRandomVerses() {
		const allLines = getAllLines();
		const filteredLines = allLines.filter(l => selectedBooks.includes(l.book));
		
		if (filteredLines.length === 0) {
			alert('Please select at least one book!');
			return;
		}

		// Find a random starting point that has enough lines available
		const maxStartIndex = filteredLines.length - lineCount;
		if (maxStartIndex < 0) {
			alert(`Not enough lines available! Only ${filteredLines.length} lines in total.`);
			return;
		}

		const randomIndex = Math.floor(Math.random() * (maxStartIndex + 1));
		const selectedLines = filteredLines.slice(randomIndex, randomIndex + lineCount);
		
		// Find the actual index in the full allLines array
		const firstLine = selectedLines[0];
		const startIndex = allLines.findIndex(l => 
			l.line === firstLine.line && 
			l.book === firstLine.book && 
			(language === 'latin' ? l.lineNumber === firstLine.lineNumber : true)
		);
		
		// Create verse from selected lines
		selectedVerse = {
			book: selectedLines[0].book,
			line_numbers: language === 'latin' ? 
				[selectedLines[0].lineNumber!, selectedLines[selectedLines.length - 1].lineNumber!] : 
				[0, 0],
			paragraphs: [selectedLines.map(l => l.line)],
			id: `custom_${startIndex}`,
			correspondingIds: [],
			corresponding: []
		};

		startLineNumber = language === 'latin' ? selectedLines[0].lineNumber! : startIndex;
		endLineNumber = language === 'latin' ? selectedLines[selectedLines.length - 1].lineNumber! : startIndex + lineCount - 1;

		// Find corresponding verse
		const originalVerse = selectedLines[0].verse;
		selectedVerse.corresponding = originalVerse.corresponding;

		// Reset peek lines
		linesAbove = [];
		linesBelow = [];
	}

	// Load lines above
	function loadLinesAbove() {
		const allLines = getAllLines();
		let firstLineIndex: number;
		
		if (language === 'latin') {
			firstLineIndex = allLines.findIndex(l => l.lineNumber === startLineNumber && l.book === selectedVerse?.book);
		} else {
			firstLineIndex = startLineNumber;
		}
		
		if (firstLineIndex > 0) {
			const startIdx = Math.max(0, firstLineIndex - peekAboveCount);
			const newLines = allLines.slice(startIdx, firstLineIndex).map(l => l.line);
			linesAbove = [...newLines, ...linesAbove];
			if (startIdx < firstLineIndex) {
				startLineNumber = language === 'latin' ? allLines[startIdx].lineNumber! : startIdx;
			}
		}
	}

	// Load lines below
	function loadLinesBelow() {
		const allLines = getAllLines();
		let lastLineIndex: number;
		
		if (language === 'latin') {
			lastLineIndex = allLines.findIndex(l => l.lineNumber === endLineNumber && l.book === selectedVerse?.book);
		} else {
			lastLineIndex = endLineNumber;
		}
		
		if (lastLineIndex >= 0 && lastLineIndex < allLines.length - 1) {
			const endIdx = Math.min(allLines.length, lastLineIndex + 1 + peekBelowCount);
			const newLines = allLines.slice(lastLineIndex + 1, endIdx).map(l => l.line);
			linesBelow = [...linesBelow, ...newLines];
			if (endIdx > lastLineIndex + 1) {
				endLineNumber = language === 'latin' ? allLines[endIdx - 1].lineNumber! : endIdx - 1;
			}
		}
	}

	// Get corresponding verses in the other language
	function getCorrespondingVerses(): Verse[] {
		if (!selectedVerse) return [];
		return selectedVerse.corresponding;
	}
</script>

<div class="container">
	<header>
		<h1>Sortes Vergilianae</h1>
		<p class="subtitle">Seek wisdom from Virgil's verses</p>
	</header>

	<section class="controls">
		<h2>Configure Your Sortilege</h2>
		
		<div class="control-group">
			<strong>Language:</strong>
			<div class="language-selector">
				<button
					class="language-button"
					class:selected={language === 'latin'}
					onclick={() => language = 'latin'}
				>
					Latin
				</button>
				<button
					class="language-button"
					class:selected={language === 'english'}
					onclick={() => language = 'english'}
				>
					English (Dryden)
				</button>
			</div>
		</div>

		<div class="control-group">
			<strong>Books to include:</strong>
			<div class="book-selector">
				<button class="toggle-all" onclick={toggleAllBooks}>
					{selectedBooks.length === availableBooks.length ? 'Deselect' : 'Select'} All
				</button>
				{#each availableBooks as book (book)}
					<button
						class="book-button"
						class:selected={selectedBooks.includes(book)}
						onclick={() => toggleBook(book)}
					>
						{book}
					</button>
				{/each}
			</div>
		</div>

		<div class="control-group">
			<label>
				<strong>Number of lines:</strong>
				<input type="number" bind:value={lineCount} min="1" max="50" />
			</label>
		</div>

		<button class="pick-button" onclick={pickRandomVerses}>
			🎲 Draw Your Fate
		</button>
	</section>

	{#if selectedVerse}
		<section class="results">
			<h2>Your Verse</h2>
			
			{#if linesAbove.length > 0}
				<div class="peek-lines peek-above">
					{#each linesAbove as line, idx (idx)}
						<div class="verse-line peek-line">{line}</div>
					{/each}
				</div>
			{/if}

			<div class="peek-button-container above">
				<button class="peek-button" onclick={loadLinesAbove}>
					↑ Show 
					<input 
						type="number" 
						bind:value={peekAboveCount} 
						min="1" 
						max="20" 
						onclick={(e) => e.stopPropagation()}
					/>
					lines above
				</button>
			</div>

			<div class="verse-display main">
				<div class="verse-meta">
					<strong>{language === 'latin' ? 'Latin' : 'English'}</strong> - 
					Book {selectedVerse.book}{#if language === 'latin'}, Lines {startLineNumber}-{endLineNumber}{/if}
				</div>
				<div class="verse-content main-content">
					{#each selectedVerse.paragraphs as paragraph, pIdx (pIdx)}
						{#each paragraph as line, lIdx (lIdx)}
							<div class="verse-line">{line}</div>
						{/each}
					{/each}
				</div>
			</div>

			<div class="peek-button-container below">
				<button class="peek-button" onclick={loadLinesBelow}>
					↓ Show 
					<input 
						type="number" 
						bind:value={peekBelowCount} 
						min="1" 
						max="20"
						onclick={(e) => e.stopPropagation()}
					/>
					lines below
				</button>
			</div>

			{#if linesBelow.length > 0}
				<div class="peek-lines peek-below">
					{#each linesBelow as line, idx (idx)}
						<div class="verse-line peek-line">{line}</div>
					{/each}
				</div>
			{/if}

			{#if getCorrespondingVerses().length > 0}
				<div class="corresponding-section">
					<h3>Corresponding {language === 'latin' ? 'English' : 'Latin'} Translation</h3>
				{#each getCorrespondingVerses() as verse (verse.id)}
					<div class="verse-display corresponding">
						<div class="verse-meta">
							Book {verse.book}, Lines {verse.line_numbers[0]}-{verse.line_numbers[1]}
						</div>
						<div class="verse-content">
							{#each verse.paragraphs as paragraph, pIdx (pIdx)}
								{#each paragraph as line, lIdx (lIdx)}
									<div class="verse-line">{line}</div>
								{/each}
							{/each}
						</div>
					</div>
				{/each}
				</div>
			{/if}
		</section>
	{:else}
		<section class="empty-state">
			<p>Click "Draw Your Fate" to receive your verse from Virgil's Aeneid</p>
		</section>
	{/if}
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Georgia', 'Times New Roman', serif;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		min-height: 100vh;
	}

	.container {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		text-align: center;
		color: white;
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 3rem;
		margin: 0;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
	}

	.subtitle {
		font-size: 1.2rem;
		font-style: italic;
		margin: 0.5rem 0 0 0;
		opacity: 0.9;
	}

	.controls {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		margin-bottom: 2rem;
	}

	.controls h2 {
		margin-top: 0;
		color: #667eea;
	}

	.control-group {
		margin-bottom: 1.5rem;
	}

	.control-group label {
		display: block;
		margin-bottom: 0.5rem;
	}

	.control-group strong {
		color: #333;
		margin-bottom: 0.5rem;
		display: block;
	}

	input[type="number"] {
		padding: 0.5rem;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-size: 1rem;
		width: 200px;
		transition: border-color 0.2s;
	}

	input[type="number"]:focus {
		outline: none;
		border-color: #667eea;
	}

	.language-selector {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.5rem;
	}

	.language-button {
		padding: 0.5rem 1.5rem;
		border: 2px solid #667eea;
		background: white;
		color: #667eea;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
		transition: all 0.2s;
		font-size: 1rem;
	}

	.language-button:hover {
		background: #f0f0f0;
	}

	.language-button.selected {
		background: #667eea;
		color: white;
	}

	.book-selector {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-top: 0.5rem;
	}

	.book-button {
		width: 40px;
		height: 40px;
		border: 2px solid #667eea;
		background: white;
		color: #667eea;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
		transition: all 0.2s;
	}

	.book-button:hover {
		background: #f0f0f0;
	}

	.book-button.selected {
		background: #667eea;
		color: white;
	}

	.toggle-all {
		padding: 0.5rem 1rem;
		background: #764ba2;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
		transition: background 0.2s;
	}

	.toggle-all:hover {
		background: #5a3980;
	}

	.pick-button {
		width: 100%;
		padding: 1rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 1.2rem;
		font-weight: bold;
		cursor: pointer;
		transition: transform 0.2s, box-shadow 0.2s;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.pick-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
	}

	.pick-button:active {
		transform: translateY(0);
	}

	.results {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.results h2 {
		margin-top: 0;
		color: #667eea;
		text-align: center;
	}

	.results h3 {
		color: #764ba2;
		margin-top: 2rem;
		margin-bottom: 1rem;
	}

	.verse-display {
		margin-bottom: 1.5rem;
		padding: 1.5rem;
		border-radius: 8px;
	}

	.verse-display.main {
		background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
		border: 2px solid #667eea;
	}

	.verse-display.corresponding {
		background: rgba(118, 75, 162, 0.05);
		border: 1px solid #764ba2;
	}

	.verse-meta {
		font-size: 0.9rem;
		color: #666;
		margin-bottom: 0.5rem;
	}

	.verse-content {
		font-size: 1.1rem;
		color: #333;
	}

	.verse-content.main-content {
		font-size: 1.2rem;
		font-weight: 500;
	}

	.verse-line {
		line-height: 1.8;
		margin-bottom: 0.3rem;
	}

	.verse-line.peek-line {
		color: #666;
		font-style: italic;
	}

	.peek-lines {
		padding: 1rem 1.5rem;
		background: #f8f8f8;
		border-radius: 8px;
		margin-bottom: 0.5rem;
	}

	.peek-lines.peek-above {
		margin-top: 0.5rem;
	}

	.peek-button-container {
		display: flex;
		justify-content: center;
		margin: 0.5rem 0;
	}

	.peek-button {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 0.95rem;
		cursor: pointer;
		transition: background 0.2s;
	}

	.peek-button:hover {
		background: #5568d3;
	}

	.peek-button input {
		width: 50px;
		padding: 0.25rem 0.5rem;
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 4px;
		background: rgba(255, 255, 255, 0.2);
		color: white;
		font-size: 0.9rem;
		text-align: center;
	}

	.peek-button input:focus {
		outline: none;
		background: rgba(255, 255, 255, 0.3);
	}

	.corresponding-section {
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 2px solid #eee;
	}

	.empty-state {
		background: white;
		border-radius: 12px;
		padding: 3rem;
		text-align: center;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		color: #666;
		font-style: italic;
		font-size: 1.1rem;
	}

	@media (max-width: 768px) {
		.container {
			padding: 1rem;
		}

		h1 {
			font-size: 2rem;
		}

		.controls, .results {
			padding: 1.5rem;
		}

		input[type="number"] {
			width: 100%;
		}

		.language-selector {
			flex-direction: column;
		}

		.language-button {
			width: 100%;
		}
	}
</style>
