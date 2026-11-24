<script lang="ts">
  import { onMount } from 'svelte'
  import { basket, lineText, resolve } from '$lib/basket.svelte'
  import Icon from '$lib/components/Icon.svelte'
  import Steps from '$lib/components/Steps.svelte'
  import { formatPrice, longDate, MAX_TICKETS_PER_ORDER } from '$lib/data/events'
  import { venueBySlug } from '$lib/data/venues'

  let ready = $state(false)
  let notice = $state('')

  onMount(() => {
    notice = basket.flash
    basket.flash = ''
    ready = true
  })
</script>

<svelte:head>
  <title>Your basket · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <Steps current={1} />
  <h1>Your basket</h1>
  <p class="lead">Tickets are held for you once you confirm. You pay at the box office or on the door.</p>
</section>

{#if ready}
  <section class="container basket-layout">
    {#if basket.lines.length}
      <div class="panel">
        <ul class="basket-lines">
          {#each basket.lines as line (line.key)}
            {@const found = resolve(line)}
            {#if found}
              <li class="basket-line">
                <div>
                  <p class="basket-line__title">{lineText(line)}</p>
                  <p class="muted">
                    {longDate(found.event.date)} · {venueBySlug(found.event.venue)?.name} · {found.ticket.note}
                  </p>
                </div>
                <p class="basket-line__price">{formatPrice(found.ticket.price * line.quantity)}</p>
                <button type="button" class="btn btn--ghost btn--sm" onclick={() => basket.remove(line.key)}>
                  Remove
                </button>
              </li>
            {/if}
          {/each}
        </ul>
        <p class="muted">{basket.count} of {MAX_TICKETS_PER_ORDER} tickets allowed in one order.</p>
      </div>
      <aside class="panel basket-summary" aria-labelledby="summary-title">
        <h2 id="summary-title">Summary</h2>
        <p class="summary-row"><span>Tickets</span><span>{basket.count}</span></p>
        <p class="summary-row summary-row--total">
          <span>Total</span><strong>{formatPrice(basket.subtotal)}</strong>
        </p>
        <a href="/checkout" class="btn btn--primary btn--block">Continue to checkout</a>
        <a href="/events" class="btn btn--ghost btn--block">Keep browsing</a>
      </aside>
    {:else}
      <div class="empty-state">
        <h2>Your basket is empty</h2>
        <p>Find something good on, then add tickets from the event page.</p>
        <a href="/events" class="btn btn--primary">See what’s on</a>
      </div>
    {/if}
  </section>
{/if}

<ul class="toasts">
  {#if notice}
    <li class="toast" role="status">
      <p>{notice}</p>
      <button type="button" class="icon-btn" aria-label="Dismiss" onclick={() => (notice = '')}>
        <Icon name="close" />
      </button>
    </li>
  {/if}
</ul>
