<script lang="ts">
  import { type Event, formatPrice, fromPrice, longDate } from '$lib/data/events'
  import { venueBySlug } from '$lib/data/venues'
  import Icon from './Icon.svelte'
  import Poster from './Poster.svelte'

  let { events }: { events: Event[] } = $props()
  let index = $state(0)
  const go = (next: number) => (index = (next + events.length) % events.length)
</script>

<section class="carousel" aria-roledescription="carousel" aria-label="Coming up">
  <div class="carousel__viewport">
    <ul class="carousel__track" style={`transform: translateX(-${index * 100}%)`}>
      {#each events as event, position (event.slug)}
        <li
          class="carousel__slide"
          role="group"
          aria-roledescription="slide"
          aria-label={`${position + 1} of ${events.length}`}
          aria-hidden={position !== index}
          inert={position !== index}
        >
          <Poster genre={event.genre} hue={event.hue} wide />
          <div class="carousel__caption">
            <p class="kicker">{longDate(event.date)} · {venueBySlug(event.venue)?.name}</p>
            <h3>{event.title}</h3>
            <p>{event.summary}</p>
            <a class="btn btn--bulb" href={`/events/${event.slug}`}>
              Tickets from {formatPrice(fromPrice(event))}
            </a>
          </div>
        </li>
      {/each}
    </ul>
  </div>
  <div class="carousel__controls">
    <button type="button" class="icon-btn" aria-label="Previous event" onclick={() => go(index - 1)}>
      <Icon name="arrow-left" />
    </button>
    <button type="button" class="icon-btn" aria-label="Next event" onclick={() => go(index + 1)}>
      <Icon name="arrow-right" />
    </button>
    <ol class="carousel__dots">
      {#each events as event, position (event.slug)}
        <li>
          <button
            type="button"
            class="carousel__dot"
            aria-label={`Show ${event.title}`}
            aria-current={position === index}
            onclick={() => (index = position)}
          ></button>
        </li>
      {/each}
    </ol>
  </div>
</section>
