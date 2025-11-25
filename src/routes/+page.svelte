<script lang="ts">
    import type { PageProps } from "./$types";
    import type { Verse } from "../../resources/load_verses";
    import { fade } from 'svelte/transition';
    import { base } from '$app/paths';

    let { data }: PageProps = $props();

    // State for user selections
    let language = $state<"latin" | "english">("latin");
    let selectedBooks = $state<number[]>([
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
    ]);

    let lineCount = $state(5);

    // State for results
    let selectedVerse = $state<Verse | null>(null);
    let linesAbove = $state<string[]>([]);
    let linesBelow = $state<string[]>([]);
    let peekAboveCount = $state(3);
    let peekBelowCount = $state(3);
    let startLineNumber = $state(0);
    let endLineNumber = $state(0);
    let showVerse = $state(false);

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
    function getAllLines(): {
        line: string;
        lineNumber?: number;
        book: number;
        verse: Verse;
    }[] {
        const verses = language === "latin" ? data.latin : data.english;
        const result: {
            line: string;
            lineNumber?: number;
            book: number;
            verse: Verse;
        }[] = [];

        if (language === "latin") {
            for (const verse of verses) {
                let currentLineNumber = verse.line_numbers[0];
                for (const paragraph of verse.paragraphs) {
                    for (const line of paragraph) {
                        result.push({
                            line,
                            lineNumber: currentLineNumber,
                            book: verse.book,
                            verse,
                        });
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
        const filteredLines = allLines.filter((l) =>
            selectedBooks.includes(l.book),
        );

        if (filteredLines.length === 0) {
            alert("Please select at least one book!");
            return;
        }

        // Find a random starting point that has enough lines available
        const maxStartIndex = filteredLines.length - lineCount;
        if (maxStartIndex < 0) {
            alert(
                `Not enough lines available! Only ${filteredLines.length} lines in total.`,
            );
            return;
        }

        const randomIndex = Math.floor(Math.random() * (maxStartIndex + 1));
        const selectedLines = filteredLines.slice(
            randomIndex,
            randomIndex + lineCount,
        );

        // Find the actual index in the full allLines array
        const firstLine = selectedLines[0];
        const startIndex = allLines.findIndex(
            (l) =>
                l.line === firstLine.line &&
                l.book === firstLine.book &&
                (language === "latin"
                    ? l.lineNumber === firstLine.lineNumber
                    : true),
        );

        // Create verse from selected lines
        selectedVerse = {
            book: selectedLines[0].book,
            line_numbers:
                language === "latin"
                    ? [
                          selectedLines[0].lineNumber!,
                          selectedLines[selectedLines.length - 1].lineNumber!,
                      ]
                    : [0, 0],
            paragraphs: [selectedLines.map((l) => l.line)],
            id: `custom_${startIndex}`,
            correspondingIds: [],
            corresponding: [],
        };

        startLineNumber =
            language === "latin" ? selectedLines[0].lineNumber! : startIndex;
        endLineNumber =
            language === "latin"
                ? selectedLines[selectedLines.length - 1].lineNumber!
                : startIndex + lineCount - 1;

        // Find corresponding verse
        const originalVerse = selectedLines[0].verse;
        selectedVerse.corresponding = originalVerse.corresponding;

        // Reset peek lines
        linesAbove = [];
        linesBelow = [];

        // Trigger animation
        showVerse = false;
        setTimeout(() => {
            showVerse = true;
        }, 50);
    }

    // Load lines above
    function loadLinesAbove() {
        const allLines = getAllLines();
        let firstLineIndex: number;

        if (language === "latin") {
            firstLineIndex = allLines.findIndex(
                (l) =>
                    l.lineNumber === startLineNumber &&
                    l.book === selectedVerse?.book,
            );
        } else {
            firstLineIndex = startLineNumber;
        }

        if (firstLineIndex > 0) {
            const startIdx = Math.max(0, firstLineIndex - peekAboveCount);
            const newLines = allLines
                .slice(startIdx, firstLineIndex)
                .map((l) => l.line);
            linesAbove = [...newLines, ...linesAbove];
            if (startIdx < firstLineIndex) {
                startLineNumber =
                    language === "latin"
                        ? allLines[startIdx].lineNumber!
                        : startIdx;
            }
        }
    }

    // Load lines below
    function loadLinesBelow() {
        const allLines = getAllLines();
        let lastLineIndex: number;

        if (language === "latin") {
            lastLineIndex = allLines.findIndex(
                (l) =>
                    l.lineNumber === endLineNumber &&
                    l.book === selectedVerse?.book,
            );
        } else {
            lastLineIndex = endLineNumber;
        }

        if (lastLineIndex >= 0 && lastLineIndex < allLines.length - 1) {
            const endIdx = Math.min(
                allLines.length,
                lastLineIndex + 1 + peekBelowCount,
            );
            const newLines = allLines
                .slice(lastLineIndex + 1, endIdx)
                .map((l) => l.line);
            linesBelow = [...linesBelow, ...newLines];
            if (endIdx > lastLineIndex + 1) {
                endLineNumber =
                    language === "latin"
                        ? allLines[endIdx - 1].lineNumber!
                        : endIdx - 1;
            }
        }
    }

    // Get corresponding verses in the other language
    function getCorrespondingVerses(): Verse[] {
        if (!selectedVerse) return [];
        return selectedVerse.corresponding;
    }

    // let correspondingVerses = $derived(getCorrespondingVerses())
    // $inspect(correspondingVerses)
</script>

<div class="container">
    <header>
        <h1><a class="title-link" href={`${base}/explanation`}>Sortes Vergilianae</a></h1>
        <p class="subtitle"><a class="subtitle-link" href={`${base}/explanation`}>Seek wisdom from Virgil's verses</a></p>
    </header>

    <section class="controls">
        <h2>Configure Your Sortilege</h2>

        <div class="control-group">
            <strong>Language:</strong>
            <div class="language-selector">
                <button
                    class="language-button"
                    class:selected={language === "latin"}
                    onclick={() => (language = "latin")}
                >
                    Latin
                </button>
                <button
                    class="language-button"
                    class:selected={language === "english"}
                    onclick={() => (language = "english")}
                >
                    English (Dryden)
                </button>
            </div>
        </div>

        <div class="control-group">
            <strong>Books to include:</strong>
            <div class="book-selector">
                <button class="toggle-all" onclick={toggleAllBooks}>
                    {selectedBooks.length === availableBooks.length
                        ? "Deselect"
                        : "Select"} All
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

            <div class="peek-button-container above">
                <button class="peek-button" onclick={loadLinesAbove}>
                    Show
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

            {#if linesAbove.length > 0}
                {#key linesAbove.length}
                    <div class="peek-lines peek-above" in:fade={{ duration: 300 }}>
                        {#each linesAbove as line, idx (idx)}
                            <div class="verse-line peek-line">{line}</div>
                        {/each}
                    </div>
                {/key}
            {/if}

            <div class="verse-display main" class:expanded={showVerse}>
                <div class="verse-meta">
                    <strong>{language === "latin" ? "Latin" : "English"}</strong
                    >
                    - Book {selectedVerse.book}{#if language === "latin"}, Lines {startLineNumber}-{endLineNumber}{/if}
                </div>
                {#key selectedVerse.id}
                    <div class="verse-content main-content" in:fade={{ duration: 600 }}>
                        {#each selectedVerse.paragraphs as paragraph, pIdx (pIdx)}
                            {#each paragraph as line, lIdx (`${pIdx}-${lIdx}`)}
                                <div class="verse-line">
                                    {line}
                                </div>
                            {/each}
                        {/each}
                    </div>
                {/key}
            </div>

            {#if linesBelow.length > 0}
                {#key linesBelow.length}
                    <div class="peek-lines peek-below" in:fade={{ duration: 300 }}>
                        {#each linesBelow as line, idx (idx)}
                            <div class="verse-line peek-line">{line}</div>
                        {/each}
                    </div>
                {/key}
            {/if}

            <div class="peek-button-container below">
                <button class="peek-button" onclick={loadLinesBelow}>
                    Show
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

            {#if getCorrespondingVerses().length > 0}
                <div class="corresponding-section">
                    <h3>
                        Corresponding {language === "latin"
                            ? "English"
                            : "Latin"} Translation
                    </h3>
                    {#each getCorrespondingVerses() as verse (verse.id)}
                        <div class="verse-display corresponding">
                            <div class="verse-meta">
                                Book {verse.book}, Lines {verse
                                    .line_numbers[0]}-{verse.line_numbers[1]}
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
            <p>
                Click "Draw Your Fate" to receive your verse from Virgil's
                Aeneid
            </p>
        </section>
    {/if}
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: "Georgia", "Times New Roman", serif;
        background: #f5f5dc;
        min-height: 100vh;
    }
    :global(button), :global(input), :global(select), :global(textarea) {
        font-family: inherit;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
    }

    header {
        text-align: center;
        color: #2c2416;
        margin-bottom: 3rem;
        padding: 2rem 0;
        border-bottom: 2px solid #8b7355;
    }

    h1 {
        font-size: 3rem;
        margin: 0;
        letter-spacing: 0.05em;
        font-weight: normal;
        text-transform: uppercase;
    }

    .subtitle {
        font-size: 1.2rem;
        font-style: italic;
        margin: 0.5rem 0 0 0;
        color: #5a4a3a;
    }

    .title-link, .subtitle-link {
        color: inherit;
        text-decoration: none;
    }

    .subtitle-link {
        border-bottom: 1px dotted #5a4a3a;
        padding-bottom: 2px;
    }

    .controls {
        background: #fefef8;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        margin-bottom: 2rem;
        border: 1px solid #d4c4a8;
    }

    .controls h2 {
        margin-top: 0;
        color: #2c2416;
        font-weight: normal;
        letter-spacing: 0.03em;
        border-bottom: 1px solid #d4c4a8;
        padding-bottom: 0.5rem;
    }

    .control-group {
        margin-bottom: 1.5rem;
    }

    .control-group label {
        display: block;
        margin-bottom: 0.5rem;
    }

    .control-group strong {
        color: #2c2416;
        margin-bottom: 0.5rem;
        display: block;
    }

    input[type="number"] {
        padding: 0.5rem;
        border: 1px solid #8b7355;
        font-size: 1rem;
        width: 200px;
        transition: border-color 0.2s;
        background: white;
    }

    input[type="number"]:focus {
        outline: none;
        border-color: #5a4a3a;
        box-shadow: 0 0 0 1px #5a4a3a;
    }

    .language-selector {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .language-button {
        padding: 0.5rem 1.5rem;
        border: 1px solid #8b7355;
        background: white;
        color: #2c2416;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.2s;
        font-size: 1rem;
    }

    .language-button:hover {
        background: #f5f5dc;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    }

    .language-button.selected {
        background: #8b7355;
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
        border: 1px solid #8b7355;
        background: white;
        color: #2c2416;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.2s;
    }

    .book-button:hover {
        background: #f5f5dc;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    }

    .book-button.selected {
        background: #8b7355;
        color: white;
    }

    .toggle-all {
        padding: 0.5rem 1rem;
        background: #5a4a3a;
        color: white;
        border: 1px solid #2c2416;
        cursor: pointer;
        font-weight: bold;
        transition: background 0.2s;
    }

    .toggle-all:hover {
        background: #3a2a1a;
    }

    .pick-button {
        width: 100%;
        padding: 1rem;
        background: #8b7355;
        color: white;
        border: 1px solid #5a4a3a;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition:
            transform 0.2s,
            box-shadow 0.2s;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.05em;
    }

    .pick-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        background: #5a4a3a;
    }

    .pick-button:active {
        transform: translateY(0);
    }

    .results {
        background: #fefef8;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        border: 1px solid #d4c4a8;
    }

    .results h2 {
        margin-top: 0;
        color: #2c2416;
        text-align: center;
        font-weight: normal;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-bottom: 1px solid #d4c4a8;
        padding-bottom: 0.5rem;
    }

    .results h3 {
        color: #5a4a3a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: normal;
        letter-spacing: 0.03em;
    }

    .verse-display {
        margin-bottom: 1.5rem;
        padding: 1.5rem;
    }

    .verse-display.main {
        /* Collapsing animation only for the main (drawn) verse */
        max-height: 0;
        overflow: hidden;
        opacity: 0;
        transition:
            max-height 0.8s ease-out,
            opacity 0.5s ease-out,
            padding 0.8s ease-out;
        background: white;
        border: 2px solid #8b7355;
        box-shadow: 
            0 3px 10px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
    }

    .verse-display.main.expanded {
        max-height: 2000px;
        opacity: 1;
        padding: 2rem;
    }

    .verse-display.corresponding {
        background: #faf9f5;
        border: 1px solid #d4c4a8;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        /* Ensure corresponding verses are always visible */
        opacity: 1;
        max-height: none;
        overflow: visible;
    }

    .verse-meta {
        font-size: 0.9rem;
        color: #5a4a3a;
        margin-bottom: 1rem;
        font-variant: small-caps;
        letter-spacing: 0.05em;
    }

    .verse-content {
        font-size: 1.1rem;
        color: #2c2416;
    }

    .verse-content.main-content {
        font-size: 1.25rem;
        font-weight: 500;
        line-height: 2;
    }

    .verse-line {
        line-height: 1.8;
        margin-bottom: 0.5rem;
    }

    .verse-line.peek-line {
        color: #7a6a5a;
        font-style: italic;
    }

    .peek-lines {
        padding: 1rem 1.5rem;
        background: #f5f5dc;
        margin-bottom: 0.5rem;
        border: 1px solid #d4c4a8;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
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
        background: #8b7355;
        color: white;
        border: 1px solid #5a4a3a;
        font-size: 0.95rem;
        cursor: pointer;
        transition: background 0.2s, box-shadow 0.2s;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    .peek-button:hover {
        background: #5a4a3a;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    }

    .peek-button input {
        width: 50px;
        padding: 0.25rem 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
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
        border-top: 2px solid #d4c4a8;
    }

    .empty-state {
        background: #fefef8;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        border: 1px solid #d4c4a8;
        color: #5a4a3a;
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

        .controls,
        .results {
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
