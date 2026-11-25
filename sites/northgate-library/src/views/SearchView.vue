<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { books } from '../data/books.js'
import { coverColour } from '../covers.js'

const route = useRoute()
const router = useRouter()

const query = computed(() => (typeof route.query.q === 'string' ? route.query.q : null))
const typed = ref(query.value ?? '')
const summary = ref(null)
const onlyAvailable = ref(false)
const floor = ref(null)

function words(text) {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
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

const shown = computed(() =>
  results.value.filter(
    (book) => (!onlyAvailable.value || book.available > 0) && (!floor.value || book.floor === floor.value),
  ),
)

function pickFloor(number) {
  floor.value = floor.value === number ? null : number
}

function search() {
  router.push({ path: '/search', query: { q: typed.value.trim() } })
}

// Keep the field in step with the address, and move focus to the result count after a search.
watch(query, async (now) => {
  typed.value = now ?? ''
  onlyAvailable.value = false
  floor.value = null
  await nextTick()
  summary.value?.focus()
})
</script>

<template>
  <span class="eyebrow">27 books on three floors</span>
  <h1 tabindex="-1">Search the catalogue</h1>
  <form class="search-form form-card" role="search" @submit.prevent="search">
    <label for="q">Title or author</label>
    <div class="search-row">
      <input id="q" v-model="typed" type="search" name="q" autocomplete="off" />
      <button class="button icon-button" type="submit">
        <svg viewBox="0 0 24 24" width="20" height="20" focusable="false">
          <circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.5" />
          <path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
        </svg>
      </button>
    </div>
  </form>

  <template v-if="query !== null">
    <h2 ref="summary" tabindex="-1">
      <template v-if="query === ''">All {{ results.length }} books</template>
      <template v-else-if="results.length === 1">1 result for “{{ query }}”</template>
      <template v-else>{{ results.length }} results for “{{ query }}”</template>
    </h2>
    <template v-if="results.length">
      <div class="chips">
        <div class="chip" :class="{ 'chip-on': onlyAvailable }" @click="onlyAvailable = !onlyAvailable">
          Available now
        </div>
        <div
          v-for="number in [1, 2, 3]"
          :key="number"
          class="chip"
          :class="{ 'chip-on': floor === number }"
          @click="pickFloor(number)"
        >
          Floor {{ number }}
        </div>
      </div>
      <p v-if="shown.length !== results.length" class="hint">
        Showing {{ shown.length }} of {{ results.length }}.
      </p>
    </template>
    <ul v-if="shown.length" class="results">
      <li v-for="book in shown" :key="book.id">
        <span class="cover" :style="{ '--cover': coverColour(book) }" aria-hidden="true"></span>
        <span>
          <RouterLink :to="`/book/${book.id}`">{{ book.title }}</RouterLink>
          <span class="byline">{{ book.author }}, {{ book.year }}</span>
        </span>
      </li>
    </ul>
    <p v-else-if="results.length">No books match these filters.</p>
    <p v-else>No books match. Try fewer words, or check the spelling.</p>
  </template>
  <p v-else>
    Type part of a title or an author’s name, or
    <RouterLink :to="{ path: '/search', query: { q: '' } }">browse the whole catalogue</RouterLink>.
  </p>
</template>
