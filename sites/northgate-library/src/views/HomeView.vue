<template>
  <h1 tabindex="-1">Welcome to Northgate Library</h1>
  <p class="lead">
    Your public library on Northgate Street, with three floors of books, quiet study rooms and a
    children's corner. Search the catalogue to see what is on the shelves, where to find it and
    how many copies are in.
  </p>
  <p><RouterLink class="button" to="/search">Search the catalogue</RouterLink></p>

  <h2>Using the library</h2>
  <ul class="plain-list">
    <li>Borrow up to eight items at a time for three weeks.</li>
    <li>Reserve any book online with your library card number. Reservations are free.</li>
    <li>Reserved books wait for you at the welcome desk on Floor 1 for seven days.</li>
    <li>Renew at the welcome desk, or return books through the drop box by the main door.</li>
  </ul>

  <h2>What's on in December</h2>
  <ul class="events">
    <li>
      <h3>Story time for under-fives</h3>
      <p>Every Saturday at 10:30, children's corner, Floor 1. No booking needed.</p>
    </li>
    <li>
      <h3>Northgate Readers book group</h3>
      <p>Thursday 10 December at 18:30, reading room, Floor 2. This month: a novel of your choice.</p>
    </li>
    <li>
      <h3>Local history drop-in</h3>
      <p>Tuesday 15 December at 14:00, local history room, Floor 3. Bring old photographs of Kelbridge.</p>
    </li>
  </ul>
</template>
