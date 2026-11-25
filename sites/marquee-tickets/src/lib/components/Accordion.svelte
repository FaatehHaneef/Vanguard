<script lang="ts" module>
  export interface Item {
    id: string
    title: string
    body: string[]
  }
</script>

<script lang="ts">
  import Icon from './Icon.svelte'

  let { items }: { items: Item[] } = $props()
  let open = $state<string | null>(null)

  $effect(() => {
    // Open the question named in the address, for links such as /faq#refunds.
    const wanted = window.location.hash.slice(1)
    if (items.some((item) => item.id === wanted)) open = wanted
  })
</script>

<div class="accordion">
  {#each items as item (item.id)}
    {@const expanded = open === item.id}
    <div class="accordion-item" id={item.id}>
      <h3>
        <button
          type="button"
          class="accordion-trigger"
          id={`${item.id}-trigger`}
          aria-expanded={expanded}
          aria-controls={`${item.id}-panel`}
          onclick={() => (open = expanded ? null : item.id)}
        >
          {item.title}
          <Icon name="plus" />
        </button>
      </h3>
      {#if expanded}
        <div
          class="accordion-panel"
          id={`${item.id}-panel`}
          role="region"
          aria-labelledby={`${item.id}-trigger`}
        >
          {#each item.body as paragraph, index (index)}
            <p>{paragraph}</p>
          {/each}
        </div>
      {/if}
    </div>
  {/each}
</div>
