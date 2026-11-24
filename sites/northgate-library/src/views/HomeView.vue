<script setup>
import { nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const typed = ref('')

function search() {
  router.push({ path: '/search', query: { q: typed.value.trim() } })
}

const features = [
  ['Borrow', 'Borrow up to eight items at a time for three weeks.'],
  ['Reserve', 'Reserve any book online with your library card number. Reservations are free.'],
  ['Collect', 'Reserved books wait for you at the welcome desk on Floor 1 for seven days.'],
  ['Return', 'Renew at the welcome desk, or return books through the drop box by the main door.'],
]

const tabs = [
  {
    id: 'december',
    label: 'In December',
    events: [
      ['Every Saturday, 10:30', 'Story time for under-fives', "Children's corner, Floor 1. No booking needed."],
      ['Thursday 10 December, 18:30', 'Northgate Readers book group', 'Reading room, Floor 2. This month: a novel of your choice.'],
      ['Tuesday 15 December, 14:00', 'Local history drop-in', 'Local history room, Floor 3. Bring old photographs of Kelbridge.'],
    ],
  },
  {
    id: 'weekly',
    label: 'Every week',
    events: [
      ['Mondays, 10:00', 'Rhyme time for babies', "Children's corner, Floor 1. Songs and rhymes for under-twos and their grown-ups."],
      ['Wednesdays, 17:00', 'Homework club', 'Study rooms, Floor 3. Quiet space and help for pupils aged 11 to 16.'],
      ['Fridays, 11:00', 'Computer help', 'Welcome desk, Floor 1. One-to-one help with email, forms and online accounts.'],
    ],
  },
]
const active = ref(tabs[0].id)
const tabButtons = ref([])

async function move(event, index) {
  const keys = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: tabs.length - 1 }
  if (!(event.key in keys)) return
  event.preventDefault()
  const next = (keys[event.key] + tabs.length) % tabs.length
  active.value = tabs[next].id
  await nextTick()
  tabButtons.value[next]?.focus()
}
</script>

<template>
  <section class="hero" aria-labelledby="welcome">
    <div>
      <span class="eyebrow">Kelbridge's public library</span>
      <h1 id="welcome" tabindex="-1">Welcome to Northgate Library</h1>
      <p class="lead">
        Your public library on Northgate Street, with three floors of books, quiet study rooms and a
        children's corner. Search the catalogue to see what is on the shelves, where to find it and
        how many copies are in.
      </p>
      <form class="hero-search" role="search" @submit.prevent="search">
        <label class="visually-hidden" for="home-q">Title or author</label>
        <input id="home-q" v-model="typed" type="search" placeholder="Title or author" autocomplete="off" />
        <button class="button" type="submit">Search</button>
      </form>
    </div>
    <svg class="hero-art" viewBox="0 0 440 300" role="img" aria-labelledby="art-title">
      <title id="art-title">Shelves of books in the reading room</title>
      <rect width="440" height="300" rx="24" fill="#f6ead2" />
      <rect x="40" y="36" width="360" height="232" rx="10" fill="#133744" />
      <g fill="#0e2a34">
        <rect x="52" y="112" width="336" height="8" />
        <rect x="52" y="190" width="336" height="8" />
      </g>
      <g>
        <rect x="62" y="56" width="18" height="56" rx="2" fill="#c8902e" />
        <rect x="82" y="64" width="14" height="48" rx="2" fill="#dcebee" />
        <rect x="98" y="52" width="22" height="60" rx="2" fill="#b04a4a" />
        <rect x="122" y="60" width="16" height="52" rx="2" fill="#6fa8b8" />
        <rect x="140" y="56" width="20" height="56" rx="2" fill="#f8f5ee" />
        <rect x="166" y="70" width="14" height="42" rx="2" fill="#c8902e" transform="rotate(-14 173 91)" />
        <rect x="196" y="58" width="18" height="54" rx="2" fill="#4f8a5b" />
        <rect x="216" y="54" width="24" height="58" rx="2" fill="#dcebee" />
        <rect x="242" y="62" width="14" height="50" rx="2" fill="#b04a4a" />
        <rect x="258" y="56" width="20" height="56" rx="2" fill="#c8902e" />
        <rect x="280" y="66" width="16" height="46" rx="2" fill="#6fa8b8" />
        <rect x="298" y="52" width="22" height="60" rx="2" fill="#f8f5ee" />
        <rect x="322" y="60" width="18" height="52" rx="2" fill="#4f8a5b" />
        <rect x="342" y="56" width="16" height="56" rx="2" fill="#b04a4a" />
        <rect x="360" y="64" width="18" height="48" rx="2" fill="#dcebee" />
      </g>
      <g>
        <rect x="62" y="138" width="22" height="52" rx="2" fill="#6fa8b8" />
        <rect x="86" y="132" width="16" height="58" rx="2" fill="#c8902e" />
        <rect x="104" y="140" width="20" height="50" rx="2" fill="#f8f5ee" />
        <rect x="126" y="134" width="14" height="56" rx="2" fill="#b04a4a" />
        <rect x="142" y="142" width="24" height="48" rx="2" fill="#4f8a5b" />
        <rect x="168" y="136" width="18" height="54" rx="2" fill="#dcebee" />
        <rect x="188" y="130" width="16" height="60" rx="2" fill="#c8902e" />
        <rect x="206" y="140" width="22" height="50" rx="2" fill="#6fa8b8" />
        <rect x="236" y="150" width="14" height="40" rx="2" fill="#b04a4a" transform="rotate(16 243 170)" />
        <rect x="262" y="134" width="20" height="56" rx="2" fill="#f8f5ee" />
        <rect x="284" y="138" width="18" height="52" rx="2" fill="#c8902e" />
        <rect x="304" y="132" width="16" height="58" rx="2" fill="#4f8a5b" />
        <rect x="322" y="140" width="22" height="50" rx="2" fill="#dcebee" />
        <rect x="346" y="136" width="18" height="54" rx="2" fill="#b04a4a" />
        <rect x="366" y="142" width="14" height="48" rx="2" fill="#6fa8b8" />
      </g>
      <g>
        <rect x="62" y="212" width="80" height="44" rx="4" fill="#c8902e" />
        <rect x="70" y="220" width="64" height="6" rx="3" fill="#f6ead2" />
        <rect x="70" y="232" width="44" height="6" rx="3" fill="#f6ead2" opacity="0.7" />
        <circle cx="330" cy="236" r="26" fill="#4f8a5b" />
        <rect x="324" y="248" width="12" height="20" fill="#7a5230" />
      </g>
    </svg>
  </section>

  <h2>Using the library</h2>
  <ul class="features">
    <li v-for="[title, text] in features" :key="title">
      <span class="feature-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="22" height="22" focusable="false">
          <path d="M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z M8 4v13" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
        </svg>
      </span>
      <h3>{{ title }}</h3>
      <p>{{ text }}</p>
    </li>
  </ul>

  <h2 id="events-heading">What's on</h2>
  <div class="tab-list" role="tablist" aria-labelledby="events-heading">
    <button
      v-for="(tab, index) in tabs"
      :id="`tab-${tab.id}`"
      :key="tab.id"
      ref="tabButtons"
      type="button"
      role="tab"
      :aria-selected="active === tab.id ? 'true' : 'false'"
      :aria-controls="`panel-${tab.id}`"
      :tabindex="active === tab.id ? 0 : -1"
      @click="active = tab.id"
      @keydown="move($event, index)"
    >
      {{ tab.label }}
    </button>
  </div>
  <div
    v-for="tab in tabs"
    v-show="active === tab.id"
    :id="`panel-${tab.id}`"
    :key="tab.id"
    role="tabpanel"
    :aria-labelledby="`tab-${tab.id}`"
  >
    <ul class="events">
      <li v-for="[when, title, where] in tab.events" :key="title">
        <span class="when">{{ when }}</span>
        <h3>{{ title }}</h3>
        <p>{{ where }}</p>
      </li>
    </ul>
  </div>
</template>
