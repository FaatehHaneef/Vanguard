<script lang="ts">
  import Carousel from '$lib/components/Carousel.svelte'
  import EventCard from '$lib/components/EventCard.svelte'
  import Icon from '$lib/components/Icon.svelte'
  import { events, genres } from '$lib/data/events'
  import { venues } from '$lib/data/venues'

  const featured = events.filter((event) => event.featured)
  const thisMonth = events.filter((event) => event.date.startsWith('2026-12')).slice(0, 4)
</script>

<svelte:head>
  <title>Marquee Tickets · Gigs, theatre and comedy in Carrick</title>
</svelte:head>

<section class="hero">
  <div class="container hero__inner">
    <div class="hero__copy">
      <p class="kicker">Carrick’s box office</p>
      <h1>Every stage in town, one box office</h1>
      <p class="lead">
        Gigs, theatre, comedy and classical concerts at the Foundry, the Corn Exchange, the Palace
        Theatre and the Lantern Rooms. No hidden fees: the price you see is the price you pay.
      </p>
      <form class="hero__search" action="/events" method="get" role="search">
        <label for="hero-q" class="visually-hidden">Search events</label>
        <Icon name="search" />
        <input id="hero-q" name="q" class="input" type="search" placeholder="Search artists, shows and venues" />
        <button type="submit" class="btn btn--bulb">Search</button>
      </form>
    </div>
    <svg class="hero__sign" viewBox="0 0 360 240" aria-hidden="true" focusable="false">
      <rect x="20" y="30" width="320" height="150" rx="14" fill="#221d3d" stroke="#ffc93c" stroke-width="4" />
      {#each Array.from({ length: 16 }, (_, i) => i) as i (i)}
        <circle cx={36 + i * 19.3} cy="44" r="4.5" fill="#ffc93c" class="bulb" style={`animation-delay: ${i * 40}ms`} />
        <circle cx={36 + i * 19.3} cy="166" r="4.5" fill="#ffc93c" class="bulb" style={`animation-delay: ${i * 40}ms`} />
      {/each}
      <text x="180" y="122" text-anchor="middle" fill="#fbfaf7" font-size="54" font-family="Anton, Impact, sans-serif" letter-spacing="4">TONIGHT</text>
      <rect x="70" y="180" width="12" height="50" fill="#322b57" />
      <rect x="278" y="180" width="12" height="50" fill="#322b57" />
    </svg>
  </div>
</section>

<section class="section" aria-labelledby="coming-up">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="kicker">Don’t miss</p>
        <h2 id="coming-up">Coming up</h2>
      </div>
      <a href="/events" class="btn btn--outline">See all events</a>
    </div>
    <Carousel events={featured} />
  </div>
</section>

<section class="section section--dark" aria-labelledby="by-genre">
  <div class="container">
    <p class="kicker kicker--bulb">Find your night</p>
    <h2 id="by-genre">Browse by genre</h2>
    <ul class="genre-grid">
      {#each genres as genre (genre.id)}
        <li>
          <a href={`/events?genre=${genre.id}`} class="genre-tile">
            <span>{genre.name}</span>
            <Icon name="arrow-right" />
          </a>
        </li>
      {/each}
    </ul>
  </div>
</section>

<section class="section" aria-labelledby="this-month">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="kicker">December</p>
        <h2 id="this-month">On sale this month</h2>
      </div>
    </div>
    <ul class="card-grid">
      {#each thisMonth as event (event.slug)}
        <EventCard {event} />
      {/each}
    </ul>
  </div>
</section>

<section class="section section--tint" aria-labelledby="venues-title">
  <div class="container">
    <h2 id="venues-title">Our venues</h2>
    <ul class="venue-strip">
      {#each venues as venue (venue.slug)}
        <li class="panel venue-strip__item">
          <span class="venue-strip__swatch" style={`background: hsl(${venue.hue} 70% 55%)`}></span>
          <h3><a href={`/venues/${venue.slug}`}>{venue.name}</a></h3>
          <p class="muted">{venue.kind} · {venue.capacity}</p>
        </li>
      {/each}
    </ul>
  </div>
</section>
