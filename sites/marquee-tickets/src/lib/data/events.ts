export type Genre = 'rock' | 'electronic' | 'jazz' | 'classical' | 'folk' | 'comedy' | 'theatre' | 'family'
export type Availability = 'available' | 'few' | 'soldout'

export interface TicketType {
  id: string
  name: string
  price: number // pence, fees included
  note: string
  availability: Availability
}

export interface Event {
  slug: string
  title: string
  genre: Genre
  venue: string // venue slug
  date: string // YYYY-MM-DD
  doors: string
  start: string
  age: string
  summary: string
  description: string[]
  tickets: TicketType[]
  hue: number
  featured?: boolean
}

export const genres: { id: Genre; name: string }[] = [
  { id: 'rock', name: 'Rock and indie' },
  { id: 'electronic', name: 'Electronic' },
  { id: 'jazz', name: 'Jazz' },
  { id: 'classical', name: 'Classical' },
  { id: 'folk', name: 'Folk and roots' },
  { id: 'comedy', name: 'Comedy' },
  { id: 'theatre', name: 'Theatre' },
  { id: 'family', name: 'Family' },
]

export const MAX_TICKETS_PER_ORDER = 6

type Tier = [name: string, price: number, availability: Availability, note: string]

function tickets(...tiers: Tier[]): TicketType[] {
  return tiers.map(([name, price, availability, note]) => ({
    id: name.toLowerCase().replace(/[^a-z]+/g, '-'),
    name,
    price,
    availability,
    note,
  }))
}

const standing = (price: number, a: Availability = 'available') =>
  ['Standard', price, a, 'Standing, general admission'] as Tier
const seated = (price: number, a: Availability = 'available') =>
  ['Standard', price, a, 'Unreserved seating'] as Tier

export const events: Event[] = [
  {
    slug: 'northern-static',
    title: 'Northern Static',
    genre: 'rock',
    venue: 'the-foundry',
    date: '2026-12-04',
    doors: '19:00',
    start: '20:00',
    age: '14+ (under 16s with an adult)',
    summary: 'The Carrick four-piece bring their second album home for one loud night.',
    description: [
      'Northern Static sold out the Lantern Rooms three times before anyone outside Carrick had heard of them. Two albums later, they come home to the Foundry with a full light show.',
      'Expect the new record in full, the old favourites at the end and a support set from Glass Harbour.',
    ],
    tickets: tickets(standing(2400), ['VIP', 4500, 'few', 'Early entry, signed poster and a drink']),
    hue: 8,
    featured: true,
  },
  {
    slug: 'velvet-arcade',
    title: 'Velvet Arcade',
    genre: 'electronic',
    venue: 'the-foundry',
    date: '2026-12-05',
    doors: '21:00',
    start: '22:00',
    age: '18+',
    summary: 'A late night of synths, strobes and analogue drum machines.',
    description: [
      'Velvet Arcade play everything live: no laptops, just racks of old synthesisers wired together on stage. Their sets run for three hours and never repeat.',
      'The bar stays open until 02:00.',
    ],
    tickets: tickets(standing(1800), ['Early bird', 1400, 'soldout', 'Standing, limited release']),
    hue: 290,
  },
  {
    slug: 'mira-okafor-trio',
    title: 'Mira Okafor Trio',
    genre: 'jazz',
    venue: 'lantern-rooms',
    date: '2026-12-10',
    doors: '19:30',
    start: '20:15',
    age: 'All ages',
    summary: 'Piano trio jazz from one of the most talked-about players in the north.',
    description: [
      'Mira Okafor’s debut was album of the year in two jazz magazines. Her trio swings hard, then turns on a dime into something quiet and strange.',
      'Table seats come with waiter service; standing tickets are at the bar.',
    ],
    tickets: tickets(
      ['Standard', 1600, 'available', 'Standing at the bar'],
      ['Premium', 2600, 'few', 'Reserved table seat'],
    ),
    hue: 210,
  },
  {
    slug: 'comedy-christmas-special',
    title: 'Chapel Lane Comedy: Christmas Special',
    genre: 'comedy',
    venue: 'lantern-rooms',
    date: '2026-12-11',
    doors: '19:00',
    start: '20:00',
    age: '18+',
    summary: 'Four comedians, one compère and a very questionable raffle.',
    description: [
      'Our monthly comedy club puts on its tinsel. Four acts from the national circuit, hosted by resident compère Jo Barraclough.',
      'Every ticket includes a raffle entry. The prizes are worse than you think.',
    ],
    tickets: tickets(['Standard', 1500, 'few', 'Unreserved seating']),
    hue: 140,
  },
  {
    slug: 'lantern-quartet',
    title: 'Lantern Quartet',
    genre: 'classical',
    venue: 'corn-exchange',
    date: '2026-12-12',
    doors: '18:45',
    start: '19:30',
    age: 'All ages',
    summary: 'Haydn, Shostakovich and a new piece written for the quartet this year.',
    description: [
      'The Lantern Quartet formed at Carrick’s music college and have toured Europe every year since. They return to the Corn Exchange with Haydn’s “Sunrise” quartet, Shostakovich’s eighth and a premiere by Helen Ashdown.',
      'There is a free pre-concert talk in the gallery at 18:50.',
    ],
    tickets: tickets(
      seated(2200),
      ['Premium', 3200, 'available', 'Front stalls, rows A to E'],
      ['Concession', 1200, 'available', 'Students and under 26s, with ID'],
    ),
    hue: 40,
    featured: true,
  },
  {
    slug: 'a-winters-tale',
    title: 'A Winter’s Tale',
    genre: 'theatre',
    venue: 'palace-theatre',
    date: '2026-12-17',
    doors: '18:45',
    start: '19:30',
    age: '12+',
    summary: 'Shakespeare’s late romance, staged in a snowbound railway station.',
    description: [
      'Carrick Players set Shakespeare’s story of jealousy and forgiveness in a station waiting room, snowed in for sixteen years. Running time is 2 hours 40 minutes with one interval.',
      'The performance is captioned.',
    ],
    tickets: tickets(
      ['Standard', 2800, 'available', 'Upper circle'],
      ['Premium', 4200, 'available', 'Stalls, rows C to L'],
      ['Concession', 1800, 'few', 'Over 65s, students and under 18s'],
    ),
    hue: 200,
    featured: true,
  },
  {
    slug: 'messiah-by-candlelight',
    title: 'Messiah by Candlelight',
    genre: 'classical',
    venue: 'corn-exchange',
    date: '2026-12-19',
    doors: '18:30',
    start: '19:15',
    age: 'All ages',
    summary: 'Handel’s Messiah with period instruments and three hundred candles.',
    description: [
      'The Carrick Bach Choir and the Northern Baroque Players perform Handel’s Messiah by candlelight, as it would have sounded in 1742.',
      'Please arrive early: the doors close when the music starts.',
    ],
    tickets: tickets(
      seated(2500, 'few'),
      ['Premium', 3800, 'soldout', 'Front stalls, rows A to E'],
      ['Concession', 1500, 'few', 'Students and under 26s, with ID'],
    ),
    hue: 30,
  },
  {
    slug: 'the-nutcracker',
    title: 'The Nutcracker',
    genre: 'family',
    venue: 'palace-theatre',
    date: '2026-12-20',
    doors: '13:15',
    start: '14:00',
    age: 'All ages',
    summary: 'The Christmas ballet, danced by the Northern Ballet School.',
    description: [
      'Clara, the Nutcracker Prince and the Sugar Plum Fairy, with Tchaikovsky’s score played live by the Palace orchestra.',
      'Children under two sit on a lap for free; please book them a free ticket at the box office.',
    ],
    tickets: tickets(
      ['Standard', 2200, 'available', 'Upper circle'],
      ['Premium', 3400, 'few', 'Stalls'],
      ['Child', 1200, 'available', 'Under 16s'],
    ),
    hue: 330,
  },
  {
    slug: 'cinderella-panto',
    title: 'Cinderella: The Pantomime',
    genre: 'family',
    venue: 'palace-theatre',
    date: '2026-12-26',
    doors: '13:15',
    start: '14:00',
    age: 'All ages',
    summary: 'Oh yes it is: the Palace pantomime is back for Boxing Day.',
    description: [
      'Ugly sisters, a pumpkin that really turns into a coach and the best slapstick routine in the county. This year’s Buttons is Carrick’s own Danny Adebayo.',
      'There is a relaxed performance with lower sound and lights on 2 January.',
    ],
    tickets: tickets(
      ['Standard', 2000, 'few', 'Upper circle'],
      ['Premium', 3000, 'available', 'Stalls'],
      ['Child', 1200, 'few', 'Under 16s'],
    ),
    hue: 300,
  },
  {
    slug: 'new-year-gala',
    title: 'Carrick Symphony: New Year Gala',
    genre: 'classical',
    venue: 'corn-exchange',
    date: '2027-01-01',
    doors: '14:15',
    start: '15:00',
    age: 'All ages',
    summary: 'Waltzes, polkas and the Radetzky March to start the year.',
    description: [
      'The Carrick Symphony’s New Year matinée has sold out every year since 2011. Strauss waltzes, polkas and a few surprises, conducted by Anja Feld.',
      'Clapping along to the Radetzky March is expected.',
    ],
    tickets: tickets(
      seated(2600),
      ['Premium', 3900, 'few', 'Front stalls, rows A to E'],
      ['Concession', 1600, 'available', 'Students and under 26s, with ID'],
    ),
    hue: 48,
    featured: true,
  },
  {
    slug: 'saltmarsh',
    title: 'Saltmarsh',
    genre: 'folk',
    venue: 'lantern-rooms',
    date: '2027-01-09',
    doors: '19:30',
    start: '20:15',
    age: 'All ages',
    summary: 'Sea shanties and fiddle tunes from the east coast, unplugged.',
    description: [
      'Five voices, a fiddle, a squeezebox and a lot of stamping. Saltmarsh sing the songs their grandparents learned on the trawlers.',
      'Singing along is very much encouraged.',
    ],
    tickets: tickets(['Standard', 1400, 'available', 'Unreserved seating']),
    hue: 180,
  },
  {
    slug: 'late-show-improv',
    title: 'The Late Show: Improv Night',
    genre: 'comedy',
    venue: 'lantern-rooms',
    date: '2027-01-14',
    doors: '20:30',
    start: '21:00',
    age: '16+',
    summary: 'A whole show made up on the spot from your suggestions.',
    description: [
      'Carrick’s longest-running improv troupe builds a musical, a murder mystery and a soap opera out of whatever the audience shouts.',
      'No two nights are the same, which is the point.',
    ],
    tickets: tickets(['Standard', 1000, 'available', 'Unreserved seating']),
    hue: 160,
  },
  {
    slug: 'neon-tide',
    title: 'Neon Tide',
    genre: 'electronic',
    venue: 'the-foundry',
    date: '2027-01-15',
    doors: '21:00',
    start: '22:00',
    age: '18+',
    summary: 'Club night with a 360-degree lighting rig and three DJs.',
    description: [
      'Neon Tide turn the Foundry into a lightbox: the stage moves to the middle of the room and the DJs play in the round until late.',
      'Last entry is at midnight.',
    ],
    tickets: tickets(standing(2000), ['VIP', 3500, 'available', 'Balcony access and a drink']),
    hue: 190,
  },
  {
    slug: 'brass-monkeys',
    title: 'The Brass Monkeys',
    genre: 'folk',
    venue: 'corn-exchange',
    date: '2027-01-16',
    doors: '19:00',
    start: '19:45',
    age: 'All ages',
    summary: 'A twelve-piece brass and folk band with a dancing tuba player.',
    description: [
      'Traditional tunes played very loudly by a band that looks like it marched in off the street. The tuba player dances. So will you.',
      'The front stalls are cleared for dancing.',
    ],
    tickets: tickets(seated(2000), ['Concession', 1200, 'available', 'Students and under 26s, with ID']),
    hue: 24,
  },
  {
    slug: 'ellis-grant-quintet',
    title: 'Sunday Jazz: Ellis Grant Quintet',
    genre: 'jazz',
    venue: 'lantern-rooms',
    date: '2027-01-17',
    doors: '17:30',
    start: '18:00',
    age: 'All ages',
    summary: 'Hard bop with a Sunday roast menu, at a civilised hour.',
    description: [
      'Saxophonist Ellis Grant and his quintet play two sets of Blakey, Morgan and their own tunes. Food is served from 17:30.',
      'Finished by 20:30, so you can make the last bus.',
    ],
    tickets: tickets(
      ['Standard', 1500, 'available', 'Standing at the bar'],
      ['Premium', 2400, 'available', 'Reserved table seat'],
    ),
    hue: 225,
  },
  {
    slug: 'dana-whitlock',
    title: 'Dana Whitlock: Overthinking It',
    genre: 'comedy',
    venue: 'palace-theatre',
    date: '2027-01-22',
    doors: '19:00',
    start: '19:45',
    age: '16+',
    summary: 'The panel show favourite’s first full-length tour.',
    description: [
      'Dana Whitlock has spent ten years on panel shows saying the thing everyone was thinking. Now she has ninety minutes to explain why.',
      'Contains strong language and an unreasonable amount of detail about her neighbours.',
    ],
    tickets: tickets(
      ['Standard', 2500, 'available', 'Upper circle'],
      ['Premium', 3200, 'available', 'Stalls'],
    ),
    hue: 110,
  },
  {
    slug: 'hollow-pines',
    title: 'Hollow Pines',
    genre: 'rock',
    venue: 'the-foundry',
    date: '2027-01-23',
    doors: '19:00',
    start: '20:00',
    age: '14+ (under 16s with an adult)',
    summary: 'Big-sky guitar rock from the band behind “Lighthouse Keeper”.',
    description: [
      'Hollow Pines write songs for long drives: slow builds, huge choruses and three guitarists. Their last tour sold out in a morning.',
      'Support comes from Carrick songwriter Ivy Mensah.',
    ],
    tickets: tickets(standing(2800, 'few'), ['VIP', 5000, 'soldout', 'Early entry, signed poster and a drink']),
    hue: 150,
  },
  {
    slug: 'harbour-lights-opening-night',
    title: 'Harbour Lights Festival: Opening Night',
    genre: 'folk',
    venue: 'corn-exchange',
    date: '2027-01-30',
    doors: '18:30',
    start: '19:15',
    age: 'All ages',
    summary: 'The winter roots festival opens with six acts on one stage.',
    description: [
      'Harbour Lights is Carrick’s winter roots festival. Opening night brings six acts to the Corn Exchange, from Gaelic song to Appalachian old-time fiddle.',
      'Festival passes are sold at the box office only.',
    ],
    tickets: tickets(
      seated(1950),
      ['Premium', 2950, 'few', 'Front stalls, rows A to E'],
      ['Concession', 1150, 'available', 'Students and under 26s, with ID'],
    ),
    hue: 205,
    featured: true,
  },
  {
    slug: 'harbour-lights-closing-night',
    title: 'Harbour Lights Festival: Closing Night',
    genre: 'folk',
    venue: 'corn-exchange',
    date: '2027-01-31',
    doors: '18:00',
    start: '18:45',
    age: 'All ages',
    summary: 'The festival’s closing ceilidh, with a caller for beginners.',
    description: [
      'The festival ends the way it always does: chairs cleared, the Harbour Lights house band on stage and a caller to walk everyone through the dances.',
      'Wear shoes you can dance in.',
    ],
    tickets: tickets(seated(1750), ['Concession', 1000, 'available', 'Students and under 26s, with ID']),
    hue: 215,
  },
  {
    slug: 'macbeth',
    title: 'Macbeth',
    genre: 'theatre',
    venue: 'palace-theatre',
    date: '2027-02-04',
    doors: '18:45',
    start: '19:30',
    age: '14+',
    summary: 'A fierce, fast Macbeth in ninety minutes without an interval.',
    description: [
      'Touring company Iron Gate Theatre strip the play down to its bones: seven actors, one bare stage and a drummer.',
      'Contains violence, haze and loud noises.',
    ],
    tickets: tickets(
      ['Standard', 2400, 'available', 'Upper circle'],
      ['Premium', 3600, 'available', 'Stalls, rows C to L'],
      ['Concession', 1600, 'available', 'Over 65s, students and under 18s'],
    ),
    hue: 0,
  },
  {
    slug: 'paper-satellites',
    title: 'Paper Satellites',
    genre: 'rock',
    venue: 'the-foundry',
    date: '2027-02-05',
    doors: '19:00',
    start: '20:00',
    age: '14+ (under 16s with an adult)',
    summary: 'Scrappy, joyful indie pop with handclaps and a horn section.',
    description: [
      'Paper Satellites are what happens when a school brass band grows up and buys guitars. Every song has a chorus you can shout.',
      'Support comes from Velvet Moths.',
    ],
    tickets: tickets(standing(2200)),
    hue: 60,
  },
  {
    slug: 'ruth-adeyemi-bach',
    title: 'Ruth Adeyemi: Bach Cello Suites',
    genre: 'classical',
    venue: 'corn-exchange',
    date: '2027-02-07',
    doors: '14:15',
    start: '15:00',
    age: 'All ages',
    summary: 'All six suites across one afternoon, with two intervals.',
    description: [
      'Cellist Ruth Adeyemi plays Bach’s six suites for solo cello in a single afternoon, as she has recorded them.',
      'Tea and cake are served in the intervals.',
    ],
    tickets: tickets(seated(2400), ['Concession', 1400, 'available', 'Students and under 26s, with ID']),
    hue: 20,
  },
  {
    slug: 'dinosaurs-live',
    title: 'Dinosaurs Live!',
    genre: 'family',
    venue: 'palace-theatre',
    date: '2027-02-13',
    doors: '10:15',
    start: '11:00',
    age: 'All ages, best for 3 to 10',
    summary: 'Life-size puppet dinosaurs, a palaeontologist and a lot of roaring.',
    description: [
      'Meet a baby triceratops, a very grumpy stegosaurus and, if you are brave, a full-size T. rex. The show lasts 55 minutes.',
      'Babies under 18 months go free on a lap.',
    ],
    tickets: tickets(['Standard', 1500, 'available', 'Upper circle'], ['Child', 1000, 'available', 'Under 16s']),
    hue: 95,
  },
  {
    slug: 'kite-season',
    title: 'Kite Season',
    genre: 'electronic',
    venue: 'the-foundry',
    date: '2027-02-20',
    doors: '19:30',
    start: '20:30',
    age: '16+',
    summary: 'Dreamy electronic pop with a string section and a choir.',
    description: [
      'Kite Season’s second album was made with a ten-piece string section and the Carrick Youth Choir, and the live show brings everyone along.',
      'This is a seated show: the floor will have chairs.',
    ],
    tickets: tickets(seated(2600), ['VIP', 4200, 'few', 'Front rows and a signed print']),
    hue: 250,
  },
  {
    slug: 'swing-big-band',
    title: 'Swing into Spring: Carrick Big Band',
    genre: 'jazz',
    venue: 'corn-exchange',
    date: '2027-02-26',
    doors: '19:00',
    start: '19:45',
    age: 'All ages',
    summary: 'Ellington, Basie and Glenn Miller with a dance floor.',
    description: [
      'Eighteen musicians, two singers and a dance floor in front of the stage. Free swing lessons start at 19:00.',
      'Dressing up is optional but popular.',
    ],
    tickets: tickets(seated(2100), ['Premium', 3100, 'available', 'Front stalls, rows A to E']),
    hue: 35,
  },
  {
    slug: 'stand-up-saturdays',
    title: 'Stand-up Saturdays',
    genre: 'comedy',
    venue: 'lantern-rooms',
    date: '2027-02-27',
    doors: '19:00',
    start: '20:00',
    age: '18+',
    summary: 'Three headliners and a newcomer, every last Saturday of the month.',
    description: [
      'The Lantern Rooms’ monthly showcase: three comedians you will have seen on television and one you will see on it soon.',
      'Seats are unreserved, so arrive early for the front.',
    ],
    tickets: tickets(['Standard', 1600, 'available', 'Unreserved seating']),
    hue: 125,
  },
]

export function eventBySlug(slug: string): Event | undefined {
  return events.find((event) => event.slug === slug)
}

export function genreName(id: Genre): string {
  return genres.find((genre) => genre.id === id)?.name ?? id
}

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

/** "Saturday 12 December 2026" */
export function longDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay()
  return `${DAYS[weekday]} ${day} ${MONTHS[month - 1]} ${year}`
}

/** "Sat 12 Dec" */
export function shortDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay()
  return `${DAYS[weekday].slice(0, 3)} ${day} ${MONTHS[month - 1].slice(0, 3)}`
}

/** "December 2026" for the month filter. */
export function monthOf(iso: string): string {
  const [year, month] = iso.split('-').map(Number)
  return `${MONTHS[month - 1]} ${year}`
}

export function fromPrice(event: Event): number {
  return Math.min(...event.tickets.filter((t) => t.availability !== 'soldout').map((t) => t.price))
}

export function formatPrice(pence: number): string {
  return `£${(pence / 100).toFixed(2)}`
}
