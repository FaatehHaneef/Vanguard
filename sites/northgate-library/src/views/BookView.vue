<script setup>
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { findBook } from '../data/books.js'
import { coverColour } from '../covers.js'

const route = useRoute()
const book = computed(() => findBook(route.params.id))

watchEffect(() => {
  document.title = `${book.value ? book.value.title : 'Book not found'} | Northgate Library`
})
</script>

<template>
  <div v-if="book" class="book-page">
    <div class="book-main">
      <p class="crumbs"><RouterLink to="/search">Back to search</RouterLink></p>
      <span class="cover large" :style="{ '--cover': coverColour(book) }" aria-hidden="true"></span>
      <h1 tabindex="-1">{{ book.title }}</h1>
      <p class="byline">{{ book.author }}, {{ book.year }}</p>
      <p class="about">{{ book.about }}</p>

      <dl class="facts">
        <dt>Author</dt>
        <dd>{{ book.author }}</dd>
        <dt>Published</dt>
        <dd>{{ book.year }}</dd>
        <dt>Availability</dt>
        <dd><span class="dot" :class="book.available > 0 ? 'dot-in' : 'dot-out'"></span></dd>
      </dl>
      <p><RouterLink class="button" :to="`/reserve/${book.id}`">Reserve</RouterLink></p>
      <p class="stock-label" aria-hidden="true">Stock batch NB-7302</p>
    </div>
    <aside class="book-side" aria-labelledby="where">
      <h2 id="where">Where to find it</h2>
      <dl class="facts">
        <dt>Floor</dt>
        <dd>Floor {{ book.floor }}</dd>
        <dt>Shelf</dt>
        <dd>{{ book.shelf }}</dd>
      </dl>
    </aside>
  </div>
  <template v-else>
    <h1 tabindex="-1">Book not found</h1>
    <p>There is no book at this address. <RouterLink to="/search">Search the catalogue</RouterLink> instead.</p>
  </template>
</template>
