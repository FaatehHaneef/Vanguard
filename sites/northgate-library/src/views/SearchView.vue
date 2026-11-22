<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { books } from '../data/books.js'

const route = useRoute()
const router = useRouter()

const query = computed(() => (typeof route.query.q === 'string' ? route.query.q : null))
const typed = ref(query.value ?? '')
const summary = ref(null)

function words(text) {
  return text
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
}

const results = computed(() => {
  if (query.value === null) return []
  const wanted = words(query.value)
  return books.filter((book) => {
    const have = words(`${book.title} ${book.author}`)
    return wanted.every((word) => have.some((part) => part.startsWith(word)))
  })
})

function search() {
  router.push({ path: '/search', query: { q: typed.value.trim() } })
}

// Keep the field in step with the address, and move focus to the result count after a search.
watch(query, async (now) => {
  typed.value = now ?? ''
  await nextTick()
  summary.value?.focus()
})
</script>

<template>
  <h1 tabindex="-1">Search the catalogue</h1>
  <form class="search-form" role="search" @submit.prevent="search">
    <label for="q">Title or author</label>
    <div class="search-row">
      <input id="q" v-model="typed" type="search" name="q" autocomplete="off" />
      <button class="button" type="submit">Search</button>
    </div>
  </form>

  <template v-if="query !== null">
    <h2 ref="summary" tabindex="-1">
      <template v-if="query === ''">All {{ results.length }} books</template>
      <template v-else-if="results.length === 1">1 result for “{{ query }}”</template>
      <template v-else>{{ results.length }} results for “{{ query }}”</template>
    </h2>
    <ul v-if="results.length" class="results">
      <li v-for="book in results" :key="book.id">
        <RouterLink :to="`/book/${book.id}`">{{ book.title }}</RouterLink>
        <span class="byline">{{ book.author }}, {{ book.year }}</span>
      </li>
    </ul>
    <p v-else>No books match. Try fewer words, or check the spelling.</p>
  </template>
  <p v-else>
    Type part of a title or an author’s name, or
    <RouterLink :to="{ path: '/search', query: { q: '' } }">browse the whole catalogue</RouterLink>.
  </p>
</template>
