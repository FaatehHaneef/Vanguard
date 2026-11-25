<script lang="ts">
  let { current }: { current: 1 | 2 | 3 } = $props()
  const steps = ['Basket', 'Your details', 'Confirmed']
</script>

<ol class="stepper" aria-label="Booking progress">
  {#each steps as step, index (step)}
    <li
      class={index + 1 < current ? 'is-done' : undefined}
      aria-current={index + 1 === current ? 'step' : undefined}
    >
      {step}
    </li>
  {/each}
</ol>
