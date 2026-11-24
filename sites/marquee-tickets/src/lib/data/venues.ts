export interface Venue {
  slug: string
  name: string
  kind: string
  address: string
  capacity: string
  description: string
  gettingThere: string
  access: string
  hue: number
}

export const venues: Venue[] = [
  {
    slug: 'the-foundry',
    name: 'The Foundry',
    kind: 'Standing music venue',
    address: 'Wharf Road, Carrick CK2 7FR',
    capacity: '900 standing',
    description:
      'A converted iron foundry by the canal, with a sprung standing floor, a balcony bar and the loudest, cleanest sound system in Carrick.',
    gettingThere:
      'Ten minutes’ walk from Carrick station along the canal path. Buses 4 and 9 stop on Wharf Road. There is no car park; the Mill Street multi-storey is five minutes away.',
    access:
      'Step-free entrance on Wharf Road. A raised viewing platform has 12 spaces for wheelchair users and their companions. Accessible toilets are on the ground floor.',
    hue: 12,
  },
  {
    slug: 'corn-exchange',
    name: 'Corn Exchange',
    kind: 'Concert hall',
    address: 'Market Square, Carrick CK1 2AB',
    capacity: '650 seated',
    description:
      'A Victorian trading hall with a glass roof and a warm acoustic, home to the Carrick Symphony and most of the town’s folk and classical concerts.',
    gettingThere:
      'On Market Square, five minutes from the station. Every bus into town stops at Market Square. The Market Street car park is next door.',
    access:
      'Level access through the Market Square doors, with lift access to the gallery. Wheelchair spaces are in rows F and M. Hearing loops cover the whole hall.',
    hue: 42,
  },
  {
    slug: 'palace-theatre',
    name: 'Palace Theatre',
    kind: 'Theatre',
    address: 'Queen Street, Carrick CK1 4PT',
    capacity: '1,100 seated on three levels',
    description:
      'Carrick’s Edwardian theatre: red velvet, gold leaf and a stage big enough for touring musicals, the Christmas pantomime and family shows.',
    gettingThere:
      'At the top of Queen Street, eight minutes from the station. Buses 2 and 7 stop outside. The Queen Street car park offers evening parking for £3.',
    access:
      'Step-free access to the stalls through the side door on Bell Lane. Captioned and audio-described performances are listed on each show page.',
    hue: 350,
  },
  {
    slug: 'lantern-rooms',
    name: 'Lantern Rooms',
    kind: 'Basement club',
    address: '12 Chapel Lane, Carrick CK1 3LN',
    capacity: '220, with tables and standing',
    description:
      'A low-ceilinged basement club with candles on every table, where Carrick goes for late jazz, folk sessions and comedy nights.',
    gettingThere:
      'Off the High Street, three minutes from Market Square. Chapel Lane is pedestrianised, so the nearest drop-off is on the High Street.',
    access:
      'The club is down a flight of 18 steps, with a platform lift on request. Please call the box office before your visit so that we can have it ready.',
    hue: 265,
  },
]

export function venueBySlug(slug: string): Venue | undefined {
  return venues.find((venue) => venue.slug === slug)
}
