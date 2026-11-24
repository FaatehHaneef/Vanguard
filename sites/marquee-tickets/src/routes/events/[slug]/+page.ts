import { error } from '@sveltejs/kit'
import { eventBySlug, events } from '$lib/data/events'
import { venueBySlug } from '$lib/data/venues'
import type { EntryGenerator, PageLoad } from './$types'

export const entries: EntryGenerator = () => events.map((event) => ({ slug: event.slug }))

export const load: PageLoad = ({ params }) => {
  const event = eventBySlug(params.slug)
  const venue = event && venueBySlug(event.venue)
  if (!event || !venue) error(404, 'Event not found')
  return { event, venue }
}
