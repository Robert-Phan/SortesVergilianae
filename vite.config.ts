import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	// Ensure vite serves assets with the repository subpath on GitHub Pages
	base: '/SortesVergilianae/',
	plugins: [sveltekit()]
});
