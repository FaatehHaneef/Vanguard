<script lang="ts">
  import { goto } from '$app/navigation'
  import { basket } from '$lib/basket.svelte'
  import Icon from '$lib/components/Icon.svelte'
  import Poster from '$lib/components/Poster.svelte'
  import { formatPrice, genreName, longDate, MAX_TICKETS_PER_ORDER } from '$lib/data/events'

  let { data } = $props()
  const event = $derived(data.event)
  const venue = $derived(data.venue)

  let ticketId = $state('')
  let quantity = $state<number | null>(1)
  let error = $state('')
  const selected = $derived(event.tickets.find((t) => t.id === ticketId) ?? event.tickets[0])

  $effect(() => {
    // A new event page starts with its first ticket type and one ticket.
    ticketId = event.tickets[0].id
    quantity = 1
    error = ''
  })

  const change = (step: number) => {
    quantity = Math.max(1, (Number(quantity) || 0) + step)
    error = ''
  }

  function addToBasket(submitted: SubmitEvent) {
    submitted.preventDefault()
    const wanted = Number(quantity)
    if (!Number.isInteger(wanted) || wanted < 1) {
      error = `Enter how many tickets you want, as a number from 1 to ${MAX_TICKETS_PER_ORDER}.`
      return
    }
    if (selected.availability === 'soldout') {
      error = `Sorry, ${selected.name} tickets for this event are sold out. Please choose another ticket type.`
      return
    }
    const room = MAX_TICKETS_PER_ORDER - basket.count
    if (wanted > room) {
      error =
        basket.count === 0
          ? `You can buy up to ${MAX_TICKETS_PER_ORDER} tickets in one order. Please choose ${MAX_TICKETS_PER_ORDER} or fewer.`
          : `You can buy up to ${MAX_TICKETS_PER_ORDER} tickets in one order, and your basket already has ${basket.count}. You can add ${room} more.`
      return
    }
    basket.add(event.slug, selected.id, wanted)
    basket.flash = `Added ${wanted} ${selected.name} ${wanted === 1 ? 'ticket' : 'tickets'} for ${event.title}.`
    goto('/basket')
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

  <div class="event-layout">
  <article class="event-page__main">
    <Poster genre={event.genre} hue={event.hue} wide />
    <p class="kicker">{genreName(event.genre)}</p>
    <h1>{event.title}</h1>
    <p class="lead">{event.summary}</p>

    {#each event.description as paragraph, index (index)}
      <p>{paragraph}</p>
    {/each}
    <p class="muted">Age guidance: {event.age}.</p>

    <section class="venue-note panel" aria-labelledby="venue-title">
      <h2 id="venue-title">About the venue</h2>
      <p><strong>{venue.name}</strong>, {venue.address}. {venue.description}</p>
      <p><a href={`/venues/${venue.slug}`}>Getting there and access at {venue.name}</a></p>
    </section>
  </article>
  <aside class="booking-panel" aria-label="Date and tickets">
    <ul class="facts facts--stacked">
      <li><Icon name="calendar" /> {longDate(event.date)}</li>
      <li><Icon name="door" /> Doors {event.doors}</li>
      <li><Icon name="clock" /> Starts {event.start}</li>
      <li><Icon name="pin" /> <a href={`/venues/${venue.slug}`}>{venue.name}</a></li>
    </ul>
    <section class="booking" aria-labelledby="tickets-title">
      <h2 id="tickets-title">Tickets</h2>
      <form onsubmit={addToBasket} novalidate>
        <fieldset class="field">
          <legend>Ticket type</legend>
          <div class="radio-cards">
            {#each event.tickets as ticket (ticket.id)}
              <label class="radio-card">
                <input
                  type="radio"
                  name="ticket"
                  value={ticket.id}
                  checked={selected.id === ticket.id}
                  onchange={() => {
                    ticketId = ticket.id
                    error = ''
                  }}
                />
                <span class="radio-card__text">
                  <span class="radio-card__name">{ticket.name}</span>
                  <span class="muted">{ticket.note}</span>
                </span>
                <span class="radio-card__price">{formatPrice(ticket.price)}</span>
                <span class={`availability availability--${ticket.availability}`}></span>
              </label>
            {/each}
          </div>
          <p class="availability-key" aria-hidden="true">
            <span><span class="availability availability--available"></span> Available</span>
            <span><span class="availability availability--few"></span> Selling fast</span>
            <span><span class="availability availability--soldout"></span> Sold out</span>
          </p>
        </fieldset>
        <div class="field">
          <label for="quantity">Number of tickets</label>
          <div class="stepper-input">
            <button type="button" class="icon-btn icon-btn--round" onclick={() => change(-1)}>
              <Icon name="minus" />
            </button>
            <input
              id="quantity"
              class="input"
              type="number"
              min="1"
              inputmode="numeric"
              bind:value={quantity}
              oninput={() => (error = '')}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'booking-error' : undefined}
            />
            <button type="button" class="icon-btn icon-btn--round" onclick={() => change(1)}>
              <Icon name="plus" />
            </button>
          </div>
        </div>
        {#if error}
          <p class="alert" id="booking-error" role="alert">{error}</p>
        {/if}
        <p class="booking__total">
          <span>Total</span>
          <strong>{formatPrice(selected.price * Math.max(1, Number(quantity) || 1))}</strong>
        </p>
        <button type="submit" class="btn btn--primary btn--block">
          <Icon name="ticket" /> Add to basket
        </button>
      </form>
    </section>
  </aside>
  </div>
</div>
