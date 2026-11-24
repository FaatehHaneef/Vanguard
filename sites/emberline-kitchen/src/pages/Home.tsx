import { Link } from 'react-router'
import { Carousel } from '../components/Carousel'
import { DishCard } from '../components/DishCard'
import { dishes } from '../data/menu'
import { usePage } from '../lib/page'

const reviews = [
  {
    quote:
      'The karahi tastes exactly like the one my uncle makes in Lahore. I order it every Friday and it is always ready on time.',
    name: 'Nadia, Harwick',
  },
  {
    quote:
      'We picked up a family order for eight people and every dish was still hot when we got home. The daal is unreal.',
    name: 'Tom and Priya, Eastgate',
  },
  {
    quote:
      'Ordering on my phone took a minute. I collected on the way back from the station and was eating by half past six.',
    name: 'Joseph, Copper Street',
  },
  {
    quote:
      'Lovely, patient staff who talked me through what was gluten free. The malai tikka is gentle enough for my kids.',
    name: 'Helen, Harwick',
  },
]

function HeroArt() {
  return (
    <svg className="hero-art" viewBox="0 0 420 360" aria-hidden="true" focusable="false">
      <circle cx="220" cy="170" r="150" fill="#f4e6d0" />
      <circle cx="320" cy="70" r="36" fill="#ffd27a" opacity="0.7" />
      <path d="M120 70c-8-12 8-16 0-28M170 56c-8-12 8-16 0-28M220 70c-8-12 8-16 0-28" stroke="#a8988e" strokeWidth="6" strokeLinecap="round" fill="none" className="hero-art__steam" />
      <ellipse cx="200" cy="300" rx="160" ry="22" fill="#2a1d17" opacity="0.18" />
      <path d="M60 150h280c0 80-62 130-140 130S60 230 60 150z" fill="#2a1d17" />
      <path d="M40 150h40M320 150h40" stroke="#2a1d17" strokeWidth="14" strokeLinecap="round" />
      <ellipse cx="200" cy="150" rx="140" ry="30" fill="#c2410c" />
      <ellipse cx="200" cy="146" rx="120" ry="22" fill="#e0561a" />
      <circle cx="150" cy="142" r="14" fill="#f08a24" />
      <circle cx="210" cy="152" r="12" fill="#f08a24" />
      <circle cx="252" cy="138" r="10" fill="#ffd27a" />
      <path d="M170 132c6-8 16-8 20 0M228 138c5-7 13-7 17 0M120 152c5-6 12-6 15 0" stroke="#4c9a57" strokeWidth="6" strokeLinecap="round" fill="none" />
      <path d="M130 320c18-34 44-34 62 0M210 320c18-34 44-34 62 0" stroke="#f08a24" strokeWidth="10" strokeLinecap="round" fill="none" />
      <path d="M160 324c10-18 24-18 34 0M240 324c10-18 24-18 34 0" stroke="#ffd27a" strokeWidth="8" strokeLinecap="round" fill="none" />
    </svg>
  )
}

export function Home() {
  const heading = usePage('')
  const featured = dishes.filter((dish) => dish.featured)
  return (
    <>
      <section className="hero">
        <div className="container hero__inner">
          <div className="hero__copy">
            <p className="eyebrow">Copper Street, Harwick</p>
            <h1 ref={heading} tabIndex={-1}>
              Cooked over coals, ready when you are
            </h1>
            <p className="lead">
              Punjabi and Kashmiri dishes from our tandoor and karahi pans. Order online, choose a
              pickup time and collect from the counter. You pay when you collect.
            </p>
            <div className="hero__actions">
              <Link to="/menu" className="btn btn--primary">
                Order for pickup
              </Link>
              <Link to="/hours" className="btn btn--secondary">
                Opening hours
              </Link>
            </div>
            <ul className="hero__facts">
              <li>
                <strong>28</strong> dishes cooked to order
              </li>
              <li>
                <strong>20 min</strong> usual wait
              </li>
              <li>
                <strong>Tue to Sun</strong> from 12:00
              </li>
            </ul>
          </div>
          <HeroArt />
        </div>
      </section>

      <section className="section" aria-labelledby="featured-title">
        <div className="container">
          <div className="section-head">
            <div>
              <p className="eyebrow">This week’s favourites</p>
              <h2 id="featured-title">What Harwick is ordering</h2>
            </div>
            <Link to="/menu" className="btn btn--ghost">
              See the full menu
            </Link>
          </div>
          <ul className="card-grid">
            {featured.map((dish) => (
              <DishCard key={dish.slug} dish={dish} />
            ))}
          </ul>
        </div>
      </section>

      <section className="section section--tint" aria-labelledby="how-title">
        <div className="container">
          <p className="eyebrow">Pickup in three steps</p>
          <h2 id="how-title">How ordering works</h2>
          <ol className="how-steps">
            <li>
              <h3>Choose your dishes</h3>
              <p>Pick a size and the extras you like. Every curry is cooked fresh, so tell us how hot.</p>
            </li>
            <li>
              <h3>Pick a time</h3>
              <p>Give us your name, a phone number and the time you want to collect, the same day.</p>
            </li>
            <li>
              <h3>Collect and pay</h3>
              <p>Come to the counter, give your order number and pay by card or cash. That is it.</p>
            </li>
          </ol>
        </div>
      </section>

      <section className="section" aria-labelledby="reviews-title">
        <div className="container reviews">
          <div>
            <p className="eyebrow">Kind words</p>
            <h2 id="reviews-title">From our regulars</h2>
            <p className="muted">Reviews left at the counter and on our feedback cards.</p>
          </div>
          <Carousel
            label="Reviews"
            slides={reviews.map((review) => (
              <figure className="review">
                <blockquote>
                  <p>“{review.quote}”</p>
                </blockquote>
                <figcaption>{review.name}</figcaption>
              </figure>
            ))}
          />
        </div>
      </section>

      <section className="cta-band">
        <div className="container cta-band__inner">
          <h2>Hungry already?</h2>
          <p>Most orders are ready in about twenty minutes.</p>
          <Link to="/menu" className="btn btn--light">
            Start an order
          </Link>
        </div>
      </section>
    </>
  )
}
