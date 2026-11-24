<script lang="ts">
  import { events } from '$lib/data/events'
  import { venues } from '$lib/data/venues'

  const count = (slug: string) => events.filter((event) => event.venue === slug).length
</script>

<svelte:head>
  <title>Venues · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <p class="kicker">Where it happens</p>
  <h1>Venues</h1>
  <p class="lead">Four stages within ten minutes’ walk of Carrick station.</p>
</section>

<section class="container section venue-list">
  <ul class="card-grid">
    {#each venues as venue (venue.slug)}
      <li class="card venue-card">
        <div class="venue-card__band" style={`background: linear-gradient(120deg, hsl(${venue.hue} 60% 30%), hsl(${venue.hue} 75% 55%))`}>
          <span>{venue.kind}</span>
        </div>
        <div class="venue-card__body">
          <h2><a href={`/venues/${venue.slug}`}>{venue.name}</a></h2>
          <p>{venue.description}</p>
          <p class="muted">{venue.address} · {venue.capacity}</p>
          <p class="venue-card__count">{count(venue.slug)} upcoming events</p>
        </div>
      </li>
    {/each}
  </ul>
</section>
