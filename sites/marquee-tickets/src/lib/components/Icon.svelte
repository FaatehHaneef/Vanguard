<script lang="ts" module>
  const paths = {
    search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm9 16-4.3-4.3',
    close: 'M6 6l12 12M18 6 6 18',
    plus: 'M12 5v14M5 12h14',
    minus: 'M5 12h14',
    'chevron-down': 'M6 9l6 6 6-6',
    'arrow-left': 'M15 5l-7 7 7 7',
    'arrow-right': 'M9 5l7 7-7 7',
    ticket: 'M4 7h16v3a2 2 0 0 0 0 4v3H4v-3a2 2 0 0 0 0-4zm10 0v10',
    pin: 'M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21zm0-9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
    clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 4v5l3 2',
    calendar: 'M5 6h14v14H5zM5 10h14M9 3v4M15 3v4',
    door: 'M6 21V4h10v17M4 21h16M13 12h.01',
    basket: 'M5 9h14l-1.5 10h-11zM9 9l3-5 3 5',
    check: 'M5 12.5l4.5 4.5L19 7',
    access: 'M12 5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM6 8l6 1 6-1M12 9v5l-3 7M12 14l3 7',
  } as const
  export type IconName = keyof typeof paths
</script>

<script lang="ts">
  let { name, class: className = '' }: { name: IconName; class?: string } = $props()
</script>

<svg
  class={className}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
  focusable="false"
>
  <path d={paths[name]} />
</svg>
