<script lang="ts">
  import { afterNavigate } from '$app/navigation'
  import EventCard from '$lib/components/EventCard.svelte'
  import Icon from '$lib/components/Icon.svelte'
  import { events, type Genre, genreName, genres, monthOf } from '$lib/data/events'
  import { venueBySlug, venues } from '$lib/data/venues'

  const months = [...new Set(events.map((event) => monthOf(event.date)))]

  let query = $state('')
  let month = $state('')
  let venue = $state('')
  let genre = $state('')

  // Filters can arrive in the address, for example /events?genre=jazz or ?q=quartet.
  afterNavigate(({ to }) => {
    const params = to?.url.searchParams
    if (!params) return
    query = params.get('q') ?? ''
    genre = genres.some((g) => g.id === params.get('genre')) ? (params.get('genre') as Genre) : ''
    venue = venues.some((v) => v.slug === params.get('venue')) ? (params.get('venue') ?? '') : ''
    month = ''
  })

  const matches = (text: string) => text.toLowerCase().includes(query.trim().toLowerCase())
  const shown = $derived(
    events.filter(
      (event) =>
        (!month || monthOf(event.date) === month) &&
        (!venue || event.venue === venue) &&
        (!genre || event.genre === genre) &&
        (!query.trim() ||
          matches(event.title) ||
          matches(event.summary) ||
          matches(venueBySlug(event.venue)?.name ?? '') ||
          matches(genreName(event.genre))),
    ),
  )
  const filtered = $derived(Boolean(query.trim() || month || venue || genre))

  function reset() {
    query = ''
    month = ''
    venue = ''
    genre = ''
  }
</script>

<svelte:head>
  <title>All events · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <p class="kicker">What’s on</p>
  <h1>All events</h1>
  <p class="lead">Every show we sell tickets for, from December to February, soonest first.</p>
</section>

<section class="container listing">
  <form class="filters panel" role="search" onsubmit={(event) => event.preventDefault()}>
    <div class="field filters__search">
      <label for="q">Search</label>
      <div class="search-input">
        <Icon name="search" />
        <input id="q" class="input" type="search" placeholder="Artist, show or venue" bind:value={query} />
      </div>
    </div>
    <div class="field">
      <label for="month">Date</label>
      <select id="month" class="select" bind:value={month}>
        <option value="">Any date</option>
        {#each months as option (option)}
          <option value={option}>{option}</option>
        {/each}
      </select>
    </div>
    <div class="field">
      <label for="venue">Venue</label>
      <select id="venue" class="select" bind:value={venue}>
        <option value="">Any venue</option>
        {#each venues as option (option.slug)}
          <option value={option.slug}>{option.name}</option>
        {/each}
      </select>
    </div>
    <div class="field">
      <label for="genre">Genre</label>
      <select id="genre" class="select" bind:value={genre}>
        <option value="">Any genre</option>
        {#each genres as option (option.id)}
          <option value={option.id}>{option.name}</option>
        {/each}
      </select>
    </div>
  </form>

  <div class="listing__results">
    <div class="listing__summary">
      <p role="status">
        {shown.length === 1 ? '1 event' : `${shown.length} events`}{filtered ? ' match your search' : ''}
      </p>
      {#if filtered}
        <button type="button" class="btn btn--ghost btn--sm" onclick={reset}>Clear filters</button>
      {/if}
    </div>
    {#if shown.length}
      <ul class="card-grid">
        {#each shown as event (event.slug)}
          <EventCard {event} />
        {/each}
      </ul>
    {:else}
      <div class="empty-state">
        <h2>Nothing matches</h2>
        <p>Try another date or genre, or search for a venue such as “Foundry”.</p>
        <button type="button" class="btn btn--outline" onclick={reset}>Clear filters</button>
      </div>
    {/if}
  </div>
</section>
