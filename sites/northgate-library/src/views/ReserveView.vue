<script setup>
import { computed, nextTick, reactive, ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { findBook } from '../data/books.js'
import { saveReservation } from '../reservation.js'
import { STAFF_CODE } from '../staff.js'

const route = useRoute()
const router = useRouter()
const book = computed(() => findBook(route.params.id))

const card = ref('')
const name = ref('')
const errors = reactive({ card: '', name: '' })
const cardField = ref(null)
const nameField = ref(null)

watchEffect(() => {
  document.title = `${book.value ? `Reserve ${book.value.title}` : 'Book not found'} | Northgate Library`
})

async function reserve() {
  const digits = card.value.replace(/\s+/g, '')
  const staff = digits.toUpperCase() === STAFF_CODE
  errors.card =
    staff || /^\d{8}$/.test(digits) ? '' : 'Enter the 8-digit number from your library card.'
  errors.name = name.value.trim() ? '' : 'Enter your name.'
  if (errors.card || errors.name) {
    await nextTick()
    ;(errors.card ? cardField : nameField).value.focus()
    return
  }
  saveReservation(book.value, staff ? null : digits, name.value.trim())
  router.push('/reserved')
}
</script>

<template>
  <template v-if="book">
    <p class="crumbs"><RouterLink :to="`/book/${book.id}`">Back to {{ book.title }}</RouterLink></p>
    <h1 tabindex="-1">Reserve {{ book.title }}</h1>
    <p>
      {{ book.author }}, {{ book.year }}. Reservations are free. We will keep the book for you at
      the welcome desk on Floor 1.
    </p>

    <form class="reserve-form form-card" novalidate @submit.prevent="reserve">
      <label for="card">Library card number</label>
      <p id="card-hint" class="hint">8 digits, printed on the back of your card.</p>
      <input
        id="card"
        ref="cardField"
        v-model="card"
        inputmode="numeric"
        autocomplete="off"
        :aria-invalid="errors.card ? 'true' : 'false'"
        :aria-describedby="errors.card ? 'card-hint card-error' : 'card-hint'"
      />
      <p v-if="errors.card" id="card-error" class="error">{{ errors.card }}</p>

      <label for="name">Your name</label>
      <input
        id="name"
        ref="nameField"
        v-model="name"
        autocomplete="name"
        :aria-invalid="errors.name ? 'true' : 'false'"
        :aria-describedby="errors.name ? 'name-error' : undefined"
      />
      <p v-if="errors.name" id="name-error" class="error">{{ errors.name }}</p>

      <p class="actions"><button class="button" type="submit">Confirm reservation</button></p>
    </form>
  </template>
  <template v-else>
    <h1 tabindex="-1">Book not found</h1>
    <p>There is no book at this address. <RouterLink to="/search">Search the catalogue</RouterLink> instead.</p>
  </template>
</template>
