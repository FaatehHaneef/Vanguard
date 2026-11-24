<script lang="ts">
  import Icon from '$lib/components/Icon.svelte'
  import Poster from '$lib/components/Poster.svelte'
  import { type Availability, formatPrice, genreName, longDate } from '$lib/data/events'

  let { data } = $props()
  const event = $derived(data.event)
  const venue = $derived(data.venue)

  const availabilityText: Record<Availability, string> = {
    available: 'Available',
    few: 'Only a few left',
    soldout: 'Sold out',
  }
</script>

<svelte:head>
  <title>{event.title} · Marquee Tickets</title>
</svelte:head>

<div class="container event-page">
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <a href="/events">All events</a> <span aria-hidden="true">/</span>
    <span aria-current="page">{event.title}</span>
  </nav>

  <article class="event-page__main">
    <Poster genre={event.genre} hue={event.hue} wide />
    <p class="kicker">{genreName(event.genre)}</p>
    <h1>{event.title}</h1>
    <p class="lead">{event.summary}</p>

    <ul class="facts">
      <li><Icon name="calendar" /> {longDate(event.date)}</li>
      <li><Icon name="door" /> Doors {event.doors}</li>
      <li><Icon name="clock" /> Starts {event.start}</li>
      <li><Icon name="pin" /> <a href={`/venues/${venue.slug}`}>{venue.name}</a></li>
    </ul>

    {#each event.description as paragraph, index (index)}
      <p>{paragraph}</p>
    {/each}
    <p class="muted">Age guidance: {event.age}.</p>

    <section class="booking" aria-labelledby="tickets-title">
      <h2 id="tickets-title">Tickets</h2>
      <ul class="ticket-list">
        {#each event.tickets as ticket (ticket.id)}
          <li class="ticket-row">
            <div>
              <p class="ticket-row__name">{ticket.name}</p>
              <p class="muted">{ticket.note}</p>
            </div>
            <p class="ticket-row__price">{formatPrice(ticket.price)}</p>
            <p class="ticket-row__status">{availabilityText[ticket.availability]}</p>
          </li>
        {/each}
      </ul>
    </section>

    <section class="venue-note panel" aria-labelledby="venue-title">
      <h2 id="venue-title">About the venue</h2>
      <p><strong>{venue.name}</strong>, {venue.address}. {venue.description}</p>
      <p><a href={`/venues/${venue.slug}`}>Getting there and access at {venue.name}</a></p>
    </section>
  </article>
</div>
