<script setup>
import { nextTick, ref } from 'vue'
import { START_LOCATION, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const links = [
  ['/', 'Home'],
  ['/search', 'Search'],
  ['/hours', 'Opening hours'],
]

// After moving to another page within the site, put focus on its main heading, as a full
// page load would start reading from the top of the new page. The first load leaves focus
// where the browser puts it.
router.afterEach(async (to, from) => {
  menuOpen.value = false
  if (from === START_LOCATION || to.path === from.path) return
  await nextTick()
  document.querySelector('main h1')?.focus()
})

// Menu drawer (narrow screens): focus moves in, stays inside, and returns to the button.
const menuOpen = ref(false)
const menuButton = ref(null)
const drawer = ref(null)

async function openMenu() {
  menuOpen.value = true
  await nextTick()
  drawer.value?.querySelector('button, a')?.focus()
}

function closeMenu() {
  menuOpen.value = false
  menuButton.value?.focus()
}

function keepFocus(event) {
  if (event.key === 'Escape') return closeMenu()
  if (event.key !== 'Tab') return
  const items = drawer.value.querySelectorAll('button, a')
  const first = items[0]
  const last = items[items.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}
</script>

<template>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="bar">
      <RouterLink class="brand" to="/">
        <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true" focusable="false">
          <rect width="34" height="34" rx="9" fill="#fff" />
          <rect x="7" y="8" width="5" height="18" rx="1.5" fill="#1d4e5f" />
          <rect x="13.5" y="6" width="5" height="20" rx="1.5" fill="#c8902e" />
          <rect x="20" y="10" width="5" height="16" rx="1.5" fill="#b04a4a" transform="rotate(-12 22.5 18)" />
          <rect x="6" y="26" width="22" height="2.5" rx="1" fill="#133744" />
        </svg>
        Northgate Library
      </RouterLink>
      <nav class="main-nav" aria-label="Main">
        <ul>
          <li v-for="[to, label] in links" :key="to"><RouterLink :to="to">{{ label }}</RouterLink></li>
        </ul>
      </nav>
      <button
        ref="menuButton"
        class="menu-button"
        type="button"
        :aria-expanded="menuOpen ? 'true' : 'false'"
        aria-controls="menu-drawer"
        @click="openMenu"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
          <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
        </svg>
        Menu
      </button>
    </div>
  </header>

  <Transition name="fade">
    <div v-if="menuOpen" class="drawer-backdrop" @click="closeMenu"></div>
  </Transition>
  <Transition name="drawer">
    <div
      v-if="menuOpen"
      id="menu-drawer"
      ref="drawer"
      class="drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="menu-heading"
      @keydown="keepFocus"
    >
      <div class="drawer-head">
        <h2 id="menu-heading">Menu</h2>
        <button class="button secondary" type="button" @click="closeMenu">Close</button>
      </div>
      <nav aria-label="Main (menu)">
        <ul>
          <li v-for="[to, label] in links" :key="to"><RouterLink :to="to">{{ label }}</RouterLink></li>
          <li><RouterLink to="/about">About the library</RouterLink></li>
        </ul>
      </nav>
    </div>
  </Transition>

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
