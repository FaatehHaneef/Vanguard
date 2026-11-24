<script lang="ts">
  import Accordion from '$lib/components/Accordion.svelte'

  const items = [
    {
      id: 'how-many',
      title: 'How many tickets can I buy?',
      body: [
        'Up to 6 tickets in one order, across all events in your basket. This keeps tickets fair for everyone and stops resale. If you are booking for a larger group, call the box office on 01632 960871.',
      ],
    },
    {
      id: 'delivery',
      title: 'How do I get my tickets?',
      body: [
        'Choose e-tickets and we email them to you straight after you book; show them on your phone at the door. Or choose to collect them from the box office at the venue, from an hour before doors.',
      ],
    },
    {
      id: 'payment',
      title: 'When do I pay?',
      body: [
        'Your seats are held as soon as you book. You pay at the box office or on the door, by card or cash. We never ask for card details online.',
      ],
    },
    {
      id: 'refunds',
      title: 'Can I get a refund or swap my tickets?',
      body: [
        'If an event is cancelled or moved, you get a full refund automatically. Otherwise we can swap your tickets for another date of the same show up to 48 hours before the start, for free.',
      ],
    },
    {
      id: 'access',
      title: 'How do I book an access space?',
      body: [
        'Every venue has wheelchair spaces and free companion tickets. Call the box office so that we can book the right space and tell the venue you are coming.',
        'Each venue page lists step-free routes, hearing loops and captioned performances.',
      ],
    },
    {
      id: 'ages',
      title: 'Are there age limits?',
      body: [
        'Each event page shows the age guidance set by the artist or the venue. For 14+ and 16+ gigs, under 16s must come with an adult. 18+ means ID will be checked at the door.',
      ],
    },
    {
      id: 'late',
      title: 'What if I arrive late?',
      body: [
        'For gigs you can come in at any time. For theatre and classical concerts you will be shown to your seat at a suitable break, so please leave plenty of time.',
      ],
    },
  ]
</script>

<svelte:head>
  <title>Help · Marquee Tickets</title>
</svelte:head>

<section class="container page-head">
  <p class="kicker">Help</p>
  <h1>Questions and answers</h1>
  <p class="lead">
    Everything people ask the box office, in one place. Still stuck? Call 01632 960871, Monday to
    Saturday, 10:00 to 18:00.
  </p>
</section>

<section class="container faq">
  <Accordion {items} />
</section>
