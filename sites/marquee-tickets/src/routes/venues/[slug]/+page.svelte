<script lang="ts">
  import EventCard from '$lib/components/EventCard.svelte'

  let { data } = $props()
  const venue = $derived(data.venue)

  const tabs = [
    { id: 'whats-on', label: 'What’s on' },
    { id: 'getting-there', label: 'Getting there' },
    { id: 'access', label: 'Access' },
  ] as const
  type TabId = (typeof tabs)[number]['id']
  let tab = $state<TabId>('whats-on')
  const buttons: HTMLButtonElement[] = []

  function onKey(event: KeyboardEvent, index: number) {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
    if (!step) return
    event.preventDefault()
    const next = (index + step + tabs.length) % tabs.length
    tab = tabs[next].id
    buttons[next]?.focus()
  }
</script>

<svelte:head>
  <title>{venue.name} · Marquee Tickets</title>
</svelte:head>

<section class="venue-hero" style={`--venue-hue: ${venue.hue}`}>
  <div class="container">
    <nav class="breadcrumbs breadcrumbs--light" aria-label="Breadcrumb">
      <a href="/venues">Venues</a> <span aria-hidden="true">/</span>
      <span aria-current="page">{venue.name}</span>
    </nav>
    <p class="kicker kicker--bulb">{venue.kind}</p>
    <h1>{venue.name}</h1>
    <p class="lead">{venue.description}</p>
    <p>{venue.address} · {venue.capacity}</p>
  </div>
</section>

<section class="container section">
  <div class="tablist" role="tablist" aria-label={`About ${venue.name}`}>
    {#each tabs as item, index (item.id)}
      <button
        bind:this={buttons[index]}
        type="button"
        role="tab"
        class="tab"
        id={`tab-${item.id}`}
        aria-selected={tab === item.id}
        aria-controls={`panel-${item.id}`}
        tabindex={tab === item.id ? 0 : -1}
        onclick={() => (tab = item.id)}
        onkeydown={(event) => onKey(event, index)}
      >
        {item.label}
      </button>
    {/each}
  </div>
  <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} class="tabpanel">
    {#if tab === 'whats-on'}
      <ul class="card-grid">
        {#each data.events as event (event.slug)}
          <EventCard {event} />
        {/each}
      </ul>
    {:else if tab === 'getting-there'}
      <p class="prose">{venue.gettingThere}</p>
    {:else}
      <p class="prose">{venue.access}</p>
      <p class="prose">
        To book a wheelchair space or a companion ticket, call the box office on 01632 960871. Companion
        tickets are free.
      </p>
    {/if}
  </div>
</section>
