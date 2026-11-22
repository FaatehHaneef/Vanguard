<script setup>
import { loadReservation } from '../reservation.js'

const reservation = loadReservation()
</script>

<template>
  <template v-if="reservation">
    <h1 tabindex="-1">Reservation confirmed</h1>
    <p class="lead">
      Thank you, {{ reservation.name }}. Your reservation number is
      <strong>{{ reservation.number }}</strong>.
    </p>
    <dl class="facts">
      <dt>Book</dt>
      <dd>{{ reservation.title }}, {{ reservation.author }}</dd>
      <dt>Library card</dt>
      <dd>ending {{ reservation.cardEnd }}</dd>
      <dt>Collect from</dt>
      <dd>The reservations shelf at the welcome desk, Floor 1</dd>
    </dl>
    <p v-if="reservation.ready">
      A copy is on the shelf now. We will set it aside and keep it for you for seven days.
    </p>
    <p v-else>
      All copies are out on loan. We will keep the next copy returned for you for seven days.
    </p>
    <p>
      Bring your library card when you collect.
      <RouterLink to="/search">Search for another book</RouterLink>
    </p>
  </template>
  <template v-else>
    <h1 tabindex="-1">No reservation to show</h1>
    <p>
      We could not find a reservation made in this browser.
      <RouterLink to="/search">Search the catalogue</RouterLink> to reserve a book.
    </p>
  </template>
</template>
