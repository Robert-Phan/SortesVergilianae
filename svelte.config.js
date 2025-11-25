import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter(),
		// When deploying to GitHub Pages under a repository path,
		// set the base path so routes and assets are generated correctly.
		paths: {
			base: '/SortesVergilianae'
		}
	}
};

export default config;
