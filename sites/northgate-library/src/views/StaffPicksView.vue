<script setup>
import { findBook } from '../data/books.js'

const picks = [
  ['season-of-migration-to-the-north', 'Short, strange and unforgettable. Ask Yusuf at the welcome desk.'],
  ['wide-sargasso-sea', 'Read it straight after Jane Eyre and neither book is the same again.'],
  ['the-god-of-small-things', 'The best opening chapter on the second floor.'],
  ['silent-spring', 'Sixty years old and still the book our science group argues about most.'],
  ['the-phantom-tollbooth', 'For anyone who thinks they are too old for children’s books.'],
].map(([id, note]) => ({ book: findBook(id), note }))
</script>

<template>
  <h1 tabindex="-1">Staff picks</h1>
  <p class="lead">Books the library team recommend this season.</p>
  <ul class="results">
    <li v-for="{ book, note } in picks" :key="book.id">
      <RouterLink :to="`/book/${book.id}`">{{ book.title }}</RouterLink>
      <span class="byline">{{ book.author }}, {{ book.year }}</span>
      <p class="pick-note">{{ note }}</p>
    </li>
  </ul>
</template>
