<script lang="ts">
  import type { Genre } from '$lib/data/events'

  let { genre, hue, wide = false }: { genre: Genre; hue: number; wide?: boolean } = $props()
  const id = $derived(`p${hue}${genre}${wide ? 'w' : ''}`)
  const deep = $derived(`hsl(${hue} 55% 22%)`)
  const mid = $derived(`hsl(${hue} 70% 48%)`)
  const glow = $derived(`hsl(${(hue + 40) % 360} 90% 66%)`)
</script>

<svg class="poster" viewBox={wide ? '0 0 400 220' : '0 0 320 200'} aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color={deep} />
      <stop offset="1" stop-color={mid} />
    </linearGradient>
  </defs>
  <rect width="400" height="220" fill={`url(#${id})`} />
  <g transform={wide ? 'translate(40 10)' : 'translate(0 -10)'}>
    {#if genre === 'rock'}
      <path d="M150 30l-40 90h40l-20 70 80-110h-44l30-50z" fill={glow} />
      <circle cx="250" cy="60" r="26" fill="none" stroke={glow} stroke-width="6" opacity="0.6" />
    {:else if genre === 'electronic'}
      {#each [0, 1, 2, 3, 4] as row (row)}
        <path
          d={`M20 ${80 + row * 22} q40 -30 80 0 t80 0 t80 0 t80 0`}
          fill="none"
          stroke={glow}
          stroke-width="5"
          opacity={1 - row * 0.17}
        />
      {/each}
    {:else if genre === 'jazz'}
      <circle cx="130" cy="150" r="26" fill={glow} />
      <rect x="150" y="50" width="10" height="100" fill={glow} />
      <path d="M160 50c30 10 50 20 50 50" fill="none" stroke={glow} stroke-width="10" stroke-linecap="round" />
      <circle cx="240" cy="80" r="10" fill={glow} opacity="0.6" />
    {:else if genre === 'classical'}
      <ellipse cx="160" cy="120" rx="44" ry="62" fill={glow} />
      <ellipse cx="160" cy="120" rx="20" ry="30" fill={deep} />
      <rect x="156" y="20" width="8" height="70" fill={glow} />
      <path d="M90 60l150 120" stroke="#fff" stroke-width="3" opacity="0.7" />
    {:else if genre === 'folk'}
      <circle cx="160" cy="110" r="44" fill={glow} />
      {#each [0, 45, 90, 135, 180, 225, 270, 315] as angle (angle)}
        <rect x="156" y="36" width="8" height="18" fill={glow} transform={`rotate(${angle} 160 110)`} />
      {/each}
      <path d="M40 190c60-30 180-30 240 0" fill="none" stroke="#fff" stroke-width="4" opacity="0.5" />
    {:else if genre === 'comedy'}
      <rect x="140" y="40" width="40" height="70" rx="20" fill={glow} />
      <path d="M120 100a40 40 0 0 0 80 0" fill="none" stroke={glow} stroke-width="8" />
      <rect x="156" y="140" width="8" height="40" fill={glow} />
      <rect x="130" y="178" width="60" height="8" rx="4" fill={glow} />
    {:else if genre === 'theatre'}
      <path d="M90 60h90v50a45 45 0 0 1-90 0z" fill={glow} />
      <circle cx="115" cy="85" r="8" fill={deep} />
      <circle cx="155" cy="85" r="8" fill={deep} />
      <path d="M115 118q20 16 40 0" fill="none" stroke={deep} stroke-width="5" />
      <path d="M170 90h90v50a45 45 0 0 1-90 0z" fill="#fff" opacity="0.75" />
      <path d="M195 150q20-16 40 0" fill="none" stroke={deep} stroke-width="5" />
    {:else}
      <path
        d="M160 30l22 46 50 6-37 34 10 50-45-25-45 25 10-50-37-34 50-6z"
        fill={glow}
      />
      <circle cx="70" cy="60" r="10" fill="#fff" opacity="0.6" />
      <circle cx="250" cy="160" r="14" fill="#fff" opacity="0.4" />
    {/if}
  </g>
  {#each [20, 60, 100, 140, 180, 220, 260, 300, 340, 380] as x (x)}
    <circle cx={x} cy="8" r="3" fill="#ffc93c" opacity="0.85" />
  {/each}
</svg>
