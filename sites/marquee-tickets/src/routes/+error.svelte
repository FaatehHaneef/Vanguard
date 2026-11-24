<script lang="ts">
  import { page } from '$app/state'
</script>

<svelte:head>
  <title>Page not found · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <p class="kicker">Error {page.status}</p>
  <h1>That page has left the stage</h1>
  <p class="lead">The link may be out of date, or the event may have finished.</p>
  <p><a href="/events" class="btn btn--primary">See what’s on</a></p>
</section>
