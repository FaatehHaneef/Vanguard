<svg class="logo-mark" viewBox="0 0 44 44" aria-hidden="true" focusable="false">
  <rect width="44" height="44" rx="10" fill="#221d3d" />
  <path
    d="M10 31V13l6 9.5L22 13l6 9.5L34 13v18"
    fill="none"
    stroke="#ffc93c"
    stroke-width="3.5"
    stroke-linejoin="round"
  />
  {#each [10, 18, 26, 34] as x (x)}
    <circle cx={x} cy="37" r="2" fill="#ffc93c" />
  {/each}
  {#each [10, 18, 26, 34] as x (x)}
    <circle cx={x} cy="7" r="2" fill="#e23d7a" />
  {/each}
</svg>
