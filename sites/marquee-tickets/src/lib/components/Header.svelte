<script lang="ts">
  import { page } from '$app/state'
  import { basket } from '$lib/basket.svelte'
  import Icon from './Icon.svelte'
  import Logo from './Logo.svelte'

  const links = [
    { href: '/events', label: 'All events' },
    { href: '/venues', label: 'Venues' },
    { href: '/faq', label: 'Help' },
  ]
  const current = (href: string) => page.url.pathname === href || page.url.pathname.startsWith(href + '/')
</script>

<header class="site-header">
  <div class="container site-header__inner">
    <a href="/" class="brand">
      <Logo />
      <span>Marquee<span class="brand__sub">Tickets</span></span>
    </a>
    <nav class="site-nav" aria-label="Main">
      <ul>
        {#each links as link (link.href)}
          <li>
            <a href={link.href} aria-current={current(link.href) ? 'page' : undefined}>{link.label}</a>
          </li>
        {/each}
        <li>
          <a href="/basket" class="basket-link" aria-current={current('/basket') ? 'page' : undefined}>
            <Icon name="basket" />
            Basket
            <span class="basket-link__count">{basket.count}</span>
          </a>
        </li>
      </ul>
    </nav>
  </div>
</header>
