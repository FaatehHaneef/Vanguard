<script lang="ts">
  import '@fontsource/anton/latin-400.css'
  import '@fontsource/inter/latin-400.css'
  import '@fontsource/inter/latin-600.css'
  import '@fontsource/inter/latin-700.css'
  import '@fontsource/inter/latin-800.css'
  import '$lib/styles/tokens.css'
  import '$lib/styles/base.css'
  import '$lib/styles/components.css'
  import '$lib/styles/layout.css'
  import '$lib/styles/pages.css'
  import { onMount } from 'svelte'
  import { basket } from '$lib/basket.svelte'
  import Footer from '$lib/components/Footer.svelte'
  import Header from '$lib/components/Header.svelte'

  let { children } = $props()

  // The basket lives in session storage, which only exists once the page runs in the browser.
  onMount(() => basket.load())
</script>

<a class="skip-link" href="#main">Skip to content</a>
<Header />
<main id="main">
  {@render children()}
</main>
<Footer />
