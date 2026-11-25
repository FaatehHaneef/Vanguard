import { error } from '@sveltejs/kit'
import { events } from '$lib/data/events'
import { venueBySlug, venues } from '$lib/data/venues'
import type { EntryGenerator, PageLoad } from './$types'

export const entries: EntryGenerator = () => venues.map((venue) => ({ slug: venue.slug }))

export const load: PageLoad = ({ params }) => {
  const venue = venueBySlug(params.slug)
  if (!venue) error(404, 'Venue not found')
  return { venue, events: events.filter((event) => event.venue === venue.slug) }
}
