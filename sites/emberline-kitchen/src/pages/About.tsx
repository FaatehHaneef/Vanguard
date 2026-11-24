import { useEffect } from 'react'
import { useLocation } from 'react-router'
import { Accordion } from '../components/Accordion'
import { usePage } from '../lib/page'

const team = [
  {
    initials: 'RS',
    name: 'Rukhsana Sheikh',
    role: 'Head chef and owner',
    bio: 'Cooked in family kitchens in Sialkot and Bradford before opening Emberline in 2019.',
    hue: 14,
  },
  {
    initials: 'IK',
    name: 'Imran Kaul',
    role: 'Tandoor chef',
    bio: 'Has looked after our clay oven since the first day and knows its moods better than anyone.',
    hue: 34,
  },
  {
    initials: 'GB',
    name: 'Grace Bello',
    role: 'Front of house',
    bio: 'Runs the counter, the order screen and the best playlist on Copper Street.',
    hue: 200,
  },
  {
    initials: 'DM',
    name: 'Danyal Mir',
    role: 'Pastry and desserts',
    bio: 'Makes the kulfi by hand every morning and is quietly proud of his gajar halwa.',
    hue: 280,
  },
]

const questions = [
  {
    title: 'Do you deliver?',
    body: (
      <p>
        Not at the moment. We cook for pickup only, so your food comes to you straight from the
        pan. Order online and collect from the counter.
      </p>
    ),
  },
  {
    title: 'How do I pay?',
    body: (
      <p>
        You pay when you collect, by card, phone or cash. We never ask for card details online.
      </p>
    ),
  },
  {
    title: 'Can you cater for allergies?',
    body: (
      <p>
        Our menu marks gluten-free dishes and dishes with nuts. Our kitchen handles nuts, gluten,
        dairy and mustard, so we cannot promise any dish is free of traces. Call us on 01632 960214
        before ordering if you have a severe allergy.
      </p>
    ),
  },
  {
    title: 'Can I order for a large group?',
    body: (
      <p>
        Yes. For more than twelve people, please call a day ahead so that we can marinate enough
        for everyone.
      </p>
    ),
  },
  {
    title: 'How hot is “hot”?',
    body: (
      <p>
        Mild has no fresh chilli. Medium is how most of our regulars eat. Hot has a proper kick, and
        Extra hot is for people who already know they want it.
      </p>
    ),
  },
]

export function About() {
  const heading = usePage('About us')
  const { hash } = useLocation()
  useEffect(() => {
    if (hash) document.getElementById(hash.slice(1))?.scrollIntoView()
  }, [hash])

  return (
    <>
      <section className="container page-head about-head">
        <p className="eyebrow">Since 2019</p>
        <h1 ref={heading} tabIndex={-1}>
          A small kitchen with a big clay oven
        </h1>
        <p className="lead">
          Emberline started as a Friday-night karahi stall at Harwick market. Five years on we have
          a counter on Copper Street, a tandoor that never quite cools down and a menu that still
          fits on one page.
        </p>
      </section>

      <section className="container section about-values" aria-labelledby="values-title">
        <h2 id="values-title">What we care about</h2>
        <ul className="card-grid">
          <li className="panel">
            <h3>Cooked to order</h3>
            <p>Nothing sits under a heat lamp. Your dish goes into the pan when your order comes in.</p>
          </li>
          <li className="panel">
            <h3>Fire, not fryers</h3>
            <p>Most of the menu is cooked over charcoal or in the tandoor. You can taste the smoke.</p>
          </li>
          <li className="panel">
            <h3>Local suppliers</h3>
            <p>Our lamb comes from Bryn farm, our dairy from Harwick Vale and our bread flour from Mill Lane.</p>
          </li>
        </ul>
      </section>

      <section className="section section--tint" aria-labelledby="team-title">
        <div className="container">
          <h2 id="team-title">The people at the pass</h2>
          <ul className="card-grid team-grid">
            {team.map((person) => (
              <li className="card team-card" key={person.name}>
                <span
                  className="team-card__avatar"
                  style={{ background: `hsl(${person.hue} 60% 88%)`, color: `hsl(${person.hue} 60% 30%)` }}
                  aria-hidden="true"
                >
                  {person.initials}
                </span>
                <h3>{person.name}</h3>
                <p className="team-card__role">{person.role}</p>
                <p>{person.bio}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="container section" id="questions" aria-labelledby="questions-title">
        <h2 id="questions-title">Questions we hear a lot</h2>
        <Accordion items={questions} />
      </section>
    </>
  )
}
