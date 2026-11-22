<script setup>
import { nextTick } from 'vue'
import { START_LOCATION, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// After moving to another page within the site, put focus on its main heading, as a full
// page load would start reading from the top of the new page. The first load leaves focus
// where the browser puts it.
router.afterEach(async (to, from) => {
  if (from === START_LOCATION || to.path === from.path) return
  await nextTick()
  document.querySelector('main h1')?.focus()
})
</script>

<template>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="bar">
      <RouterLink class="brand" to="/">Northgate Library</RouterLink>
      <nav aria-label="Main">
        <ul>
          <li><RouterLink to="/">Home</RouterLink></li>
          <li><RouterLink to="/search">Search</RouterLink></li>
          <li><RouterLink to="/hours">Opening hours</RouterLink></li>
        </ul>
      </nav>
    </div>
  </header>
  <main id="main" tabindex="-1" :class="{ wide: route.meta.wide }">
    <RouterView />
  </main>
  <footer class="site-footer">
    <div class="bar">
      <nav aria-label="Footer">
        <ul>
          <li><RouterLink to="/search">Search the catalogue</RouterLink></li>
          <li><RouterLink to="/hours">Opening hours</RouterLink></li>
          <li><RouterLink to="/about">About the library</RouterLink></li>
        </ul>
      </nav>
      <p>Northgate Library, 14 Northgate Street, Kelbridge</p>
      <p>This is a demonstration website. It does not hold real library accounts or loans.</p>
      <p class="footer-ref">Catalogue reference NC-5619</p>
    </div>
  </footer>
</template>
