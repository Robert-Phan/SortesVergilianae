import { loadVersesJSON } from '../../resources/load_verses';
import type { PageServerLoad } from './$types';

export const prerender = true;

export const load: PageServerLoad = async () => {
	const { latin, english } = await loadVersesJSON(
		'resources/latin_verses.json',
		'resources/english_verses.json'
	);

	return {
		latin,
		english
	};
};
