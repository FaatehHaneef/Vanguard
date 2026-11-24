<script lang="ts">
  import { onMount } from 'svelte'
  import { type Booking, lastBooking } from '$lib/basket.svelte'
  import Steps from '$lib/components/Steps.svelte'
  import { formatPrice, longDate } from '$lib/data/events'
  import { venueBySlug } from '$lib/data/venues'

  let ready = $state(false)
  let booking = $state<Booking | null>(null)
  onMount(() => {
    booking = lastBooking()
    ready = true
  })
</script>

<svelte:head>
  <title>Booking confirmed · Marquee Tickets</title>
</svelte:head>

{#if ready}
  {#if booking}
    <section class="container page-head">
      <Steps current={3} />
      <p class="kicker">Booking reference {booking.reference}</p>
      <h1>You’re going!</h1>
      <p class="lead">
        {#if booking.delivery === 'email'}
          We have emailed your e-tickets to {booking.email}. Show them on your phone at the door.
        {:else}
          Collect your tickets from the box office at the venue, from an hour before doors. Bring
          this booking reference.
        {/if}
      </p>
    </section>
    <section class="container basket-layout">
      <div class="panel">
        <h2>Your tickets</h2>
        <ul class="basket-lines">
          {#each booking.lines as line, index (index)}
            <li class="basket-line">
              <div>
                <p class="basket-line__title">{line.title} · {line.quantity} × {line.ticket}</p>
                <p class="muted">{longDate(line.date)} · {venueBySlug(line.venue)?.name}</p>
              </div>
              <p class="basket-line__price">{formatPrice(line.price)}</p>
            </li>
          {/each}
        </ul>
      </div>
      <aside class="panel basket-summary">
        <h2>Payment</h2>
        {#if booking.discount > 0}
          <p class="summary-row"><span>Discount</span><span>−{formatPrice(booking.discount)}</span></p>
        {/if}
        <p class="summary-row summary-row--total">
          <span>To pay at the box office</span><strong>{formatPrice(booking.total)}</strong>
        </p>
        <p class="muted">Booked for {booking.name}. Card and cash are accepted at every venue.</p>
        <a href="/events" class="btn btn--outline btn--block">Find another night out</a>
      </aside>
    </section>
  {:else}
    <section class="container page-head">
      <h1>No booking yet</h1>
      <p class="lead">Bookings made in this browser tab show up here.</p>
      <a href="/events" class="btn btn--primary">See what’s on</a>
    </section>
  {/if}
{/if}
