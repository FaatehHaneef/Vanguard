import { type ReactNode, useState } from 'react'
import { Icon } from './Icon'

/** A carousel moved only by its buttons: it never advances on its own. */
export function Carousel({ label, slides }: { label: string; slides: ReactNode[] }) {
  const [index, setIndex] = useState(0)
  const go = (next: number) => setIndex((next + slides.length) % slides.length)
  return (
    <section className="carousel" aria-roledescription="carousel" aria-label={label}>
      <div className="carousel-viewport">
        <ul className="carousel-track" style={{ transform: `translateX(-${index * 100}%)` }}>
          {slides.map((slide, position) => (
            <li
              className="carousel-slide"
              key={position}
              role="group"
              aria-roledescription="slide"
              aria-label={`${position + 1} of ${slides.length}`}
              aria-hidden={position !== index}
              inert={position !== index}
            >
              {slide}
            </li>
          ))}
        </ul>
      </div>
      <div className="carousel-controls">
        <button
          type="button"
          className="icon-btn"
          aria-label="Previous review"
          onClick={() => go(index - 1)}
        >
          <Icon name="arrow-left" />
        </button>
        <button type="button" className="icon-btn" aria-label="Next review" onClick={() => go(index + 1)}>
          <Icon name="arrow-right" />
        </button>
        <ul className="carousel-dots">
          {slides.map((_, position) => (
            <li key={position}>
              <button
                type="button"
                className="carousel-dot"
                aria-label={`Show review ${position + 1}`}
                aria-current={position === index}
                onClick={() => setIndex(position)}
              />
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
