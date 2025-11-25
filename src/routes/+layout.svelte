<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Sortes Vergilianes</title>
	<meta name="description" content="A digital recreation of the Sortes Vergilianes." />
</svelte:head>

{@render children()}
