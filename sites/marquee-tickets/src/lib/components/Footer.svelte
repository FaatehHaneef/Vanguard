<script lang="ts">
  import Logo from './Logo.svelte'
</script>

<footer class="site-footer">
  <div class="container site-footer__grid">
    <div>
      <a href="/" class="brand brand--light">
        <Logo />
        <span>Marquee<span class="brand__sub">Tickets</span></span>
      </a>
      <p class="site-footer__blurb">
        Tickets for every stage in Carrick, from the Foundry’s sweaty Friday gigs to Sunday
        matinées at the Palace.
      </p>
    </div>
    <nav aria-label="Venues">
      <h2 class="site-footer__title">Venues</h2>
      <ul>
        <li><a href="/venues/the-foundry">The Foundry</a></li>
        <li><a href="/venues/corn-exchange">Corn Exchange</a></li>
        <li><a href="/venues/palace-theatre">Palace Theatre</a></li>
        <li><a href="/venues/lantern-rooms">Lantern Rooms</a></li>
      </ul>
    </nav>
    <nav aria-label="Help">
      <h2 class="site-footer__title">Help</h2>
      <ul>
        <li><a href="/faq">Questions and answers</a></li>
        <li><a href="/faq#refunds">Refunds and exchanges</a></li>
        <li><a href="/faq#access">Access bookings</a></li>
      </ul>
    </nav>
    <div>
      <h2 class="site-footer__title">Box office</h2>
      <p>
        Corn Exchange foyer, Market Square, Carrick CK1 2AB
        <br />
        Monday to Saturday, 10:00 to 18:00
        <br />
        01632 960871
      </p>
    </div>
  </div>
  <div class="container site-footer__base">
    <p>© 2026 Marquee Tickets Ltd. Prices include booking fees unless stated.</p>
  </div>
</footer>
