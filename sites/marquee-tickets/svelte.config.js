import adapter from '@sveltejs/adapter-static'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Every page is rendered to HTML at build time; 404.html answers unknown paths.
    adapter: adapter({ pages: 'build', assets: 'build', fallback: '404.html', strict: true }),
    prerender: { entries: ['*', '/presale'] },
    // Only variables with these prefixes are read from the environment.
    env: { publicPrefix: 'PUBLIC_', privatePrefix: 'MARQUEE_' },
  },
}

export default config
