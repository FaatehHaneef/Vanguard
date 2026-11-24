<script lang="ts">
  import { type Event, formatPrice, fromPrice, genreName, shortDate } from '$lib/data/events'
  import { venueBySlug } from '$lib/data/venues'
  import Poster from './Poster.svelte'

  let { event }: { event: Event } = $props()
  const venue = $derived(venueBySlug(event.venue))
</script>

<li class="card event-card">
  <Poster genre={event.genre} hue={event.hue} />
  <div class="event-card__body">
    <p class="event-card__date">{shortDate(event.date)} · {event.start}</p>
    <h3 class="event-card__title">
      <a href={`/events/${event.slug}`}>{event.title}</a>
    </h3>
    <p class="event-card__venue">{venue?.name}</p>
    <p class="event-card__foot">
      <span class="chip">{genreName(event.genre)}</span>
      <span class="event-card__price">From {formatPrice(fromPrice(event))}</span>
    </p>
  </div>
</li>
