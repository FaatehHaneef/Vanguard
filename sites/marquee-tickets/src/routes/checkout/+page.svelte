<script lang="ts">
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'
  import { basket, lineText, placeBooking } from '$lib/basket.svelte'
  import { codeDiscount } from '$lib/codes'
  import Steps from '$lib/components/Steps.svelte'
  import { formatPrice } from '$lib/data/events'

  type Field = 'name' | 'email' | 'code' | 'terms'
  let ready = $state(false)
  let name = $state('')
  let email = $state('')
  let phone = $state('')
  let delivery = $state<'email' | 'box-office'>('email')
  let code = $state('')
  let terms = $state(false)
  let errors = $state<Partial<Record<Field, string>>>({})
  const fields: Partial<Record<Field, HTMLInputElement>> = $state({})

  onMount(() => (ready = true))

  const discount = $derived(codeDiscount(code, basket.subtotal) ?? 0)

  function validate(): Partial<Record<Field, string>> {
    const found: Partial<Record<Field, string>> = {}
    if (!name.trim()) found.name = 'Enter the name of the person collecting or using the tickets.'
    if (!email.trim()) found.email = 'Enter an email address so that we can send your booking.'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))
      found.email = 'Enter an email address in the right format, like name@example.com.'
    if (code.trim() && codeDiscount(code, basket.subtotal) === null) found.code = 'We do not recognise that code. Check it, or leave the box empty.'
    if (!terms) found.terms = 'Tick the box to agree to the terms of sale.'
    return found
  }

  function submit(event: SubmitEvent) {
    event.preventDefault()
    errors = validate()
    const first = (['name', 'email', 'code', 'terms'] as Field[]).find((field) => errors[field])
    if (first) {
      fields[first]?.focus()
      return
    }
    placeBooking({ name: name.trim(), email: email.trim(), phone: phone.trim(), delivery }, discount)
    goto('/confirmation')
  }
</script>

<svelte:head>
  <title>Checkout · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <Steps current={2} />
  <h1>Checkout</h1>
  <p class="lead">Who are the tickets for, and how would you like to get them?</p>
</section>

{#if ready}
  {#if basket.lines.length}
    <section class="container basket-layout">
      <form class="panel" novalidate onsubmit={submit}>
        <div class="field">
          <label for="name">Full name</label>
          <input
            id="name"
            class="input"
            autocomplete="name"
            bind:this={fields.name}
            bind:value={name}
            aria-invalid={Boolean(errors.name)}
            aria-describedby={errors.name ? 'name-error' : undefined}
          />
          {#if errors.name}<p class="field-error" id="name-error">{errors.name}</p>{/if}
        </div>
        <div class="field">
          <label for="email">Email address</label>
          <p class="hint" id="email-hint">We send your booking confirmation here.</p>
          <input
            id="email"
            class="input"
            type="email"
            autocomplete="email"
            bind:this={fields.email}
            bind:value={email}
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? 'email-hint email-error' : 'email-hint'}
          />
          {#if errors.email}<p class="field-error" id="email-error">{errors.email}</p>{/if}
        </div>
        <div class="field">
          <label for="phone">Phone number (optional)</label>
          <input id="phone" class="input" type="tel" autocomplete="tel" bind:value={phone} />
        </div>
        <fieldset class="field">
          <legend>How would you like your tickets?</legend>
          <div class="radio-cards">
            <label class="radio-card">
              <input type="radio" name="delivery" value="email" bind:group={delivery} />
              <span class="radio-card__text">
                <span class="radio-card__name">E-tickets by email</span>
                <span class="muted">Show them on your phone at the door. Free.</span>
              </span>
            </label>
            <label class="radio-card">
              <input type="radio" name="delivery" value="box-office" bind:group={delivery} />
              <span class="radio-card__text">
                <span class="radio-card__name">Collect from the box office</span>
                <span class="muted">At the venue, from an hour before doors. Free.</span>
              </span>
            </label>
          </div>
        </fieldset>
        <div class="field">
          <label for="code">Access or promo code (optional)</label>
          <input
            id="code"
            class="input input--short"
            autocomplete="off"
            bind:this={fields.code}
            bind:value={code}
            aria-invalid={Boolean(errors.code)}
            aria-describedby={errors.code ? 'code-error' : undefined}
          />
          {#if errors.code}<p class="field-error" id="code-error">{errors.code}</p>{/if}
        </div>
        <div class="field">
          <label class="check">
            <input
              type="checkbox"
              bind:this={fields.terms}
              bind:checked={terms}
              aria-invalid={Boolean(errors.terms)}
              aria-describedby={errors.terms ? 'terms-error' : undefined}
            />
            <span>I agree to the terms of sale, including the limit of 6 tickets per order.</span>
          </label>
          {#if errors.terms}<p class="field-error" id="terms-error">{errors.terms}</p>{/if}
        </div>
        <button type="submit" class="btn btn--primary btn--block">Confirm booking</button>
      </form>
      <aside class="panel basket-summary" aria-labelledby="summary-title">
        <h2 id="summary-title">Your tickets</h2>
        <ul class="summary-lines">
          {#each basket.lines as line (line.key)}
            <li>{lineText(line)}</li>
          {/each}
        </ul>
        {#if discount > 0}
          <p class="summary-row"><span>Discount</span><span>−{formatPrice(discount)}</span></p>
        {/if}
        <p class="summary-row summary-row--total">
          <span>To pay at the box office</span><strong>{formatPrice(basket.subtotal - discount)}</strong>
        </p>
        <a href="/basket" class="btn btn--ghost btn--sm">Change your basket</a>
      </aside>
    </section>
  {:else}
    <section class="container">
      <div class="empty-state">
        <h2>Your basket is empty</h2>
        <p>Add tickets from an event page first.</p>
        <a href="/events" class="btn btn--primary">See what’s on</a>
      </div>
    </section>
  {/if}
{/if}
