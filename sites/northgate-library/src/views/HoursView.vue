<script setup>
const week = [
  ['Monday', '9:00', '19:00'],
  ['Tuesday', '9:00', '19:00'],
  ['Wednesday', '9:00', '17:00'],
  ['Thursday', '9:00', '19:00'],
  ['Friday', '9:00', '17:00'],
  ['Saturday', '10:00', '16:00'],
  ['Sunday', '12:00', '16:00'],
]
</script>

<template>
  <span class="eyebrow">Open every day</span>
  <h1 tabindex="-1">Opening hours</h1>
  <p class="lead">The library is open every day of the week. The doors close at the times shown.</p>

  <div class="table-card">
  <table>
    <caption>Weekly opening hours</caption>
    <thead>
      <tr>
        <th scope="col">Day</th>
        <th scope="col">Opens</th>
        <th scope="col">Closes</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="[day, opens, closes] in week" :key="day">
        <th scope="row">{{ day }}</th>
        <td>{{ opens }}</td>
        <td>{{ closes }}</td>
      </tr>
    </tbody>
  </table>
  </div>

  <h2>Good to know</h2>
  <ul class="plain-list">
    <li>Study rooms on Floor 3 close 30 minutes before the library.</li>
    <li>The book drop by the main door is open at all times; returns are checked in the next morning.</li>
    <li>The children’s corner holds story time every Saturday at 10:30.</li>
  </ul>

  <h2>Holiday opening</h2>
  <ul class="plain-list">
    <li>Thursday 24 December 2026: 9:00 to 14:00.</li>
    <li>Friday 25 December and Saturday 26 December 2026: closed.</li>
    <li>Thursday 31 December 2026: 9:00 to 15:00.</li>
    <li>Friday 1 January 2027: closed.</li>
  </ul>
</template>
