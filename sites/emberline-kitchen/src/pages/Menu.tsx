import { type KeyboardEvent, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { DishCard } from '../components/DishCard'
import { DishDialog } from '../components/DishDialog'
import { Icon } from '../components/Icon'
import { type CategoryId, categories, dishBySlug, dishes } from '../data/menu'
import { usePage } from '../lib/page'

type Tab = 'all' | CategoryId
const tabs: { id: Tab; name: string }[] = [{ id: 'all', name: 'All dishes' }, ...categories]

function matches(query: string, text: string) {
  return text.toLowerCase().includes(query.trim().toLowerCase())
}

export function Menu() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const dish = dishBySlug(slug)
  const heading = usePage('Menu', Boolean(dish))
  const [tab, setTab] = useState<Tab>('all')
  const [query, setQuery] = useState('')
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([])

  const shown = useMemo(
    () =>
      dishes.filter(
        (dish) =>
          (tab === 'all' || dish.category === tab) &&
          (!query.trim() || matches(query, dish.name) || matches(query, dish.description)),
      ),
    [tab, query],
  )

  const onTabKey = (event: KeyboardEvent, index: number) => {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
    if (!step) return
    event.preventDefault()
    const next = (index + step + tabs.length) % tabs.length
    setTab(tabs[next].id)
    tabRefs.current[next]?.focus()
  }

  const groups = (tab === 'all' ? categories : categories.filter((c) => c.id === tab))
    .map((category) => ({ category, items: shown.filter((dish) => dish.category === category.id) }))
    .filter((group) => group.items.length)

  return (
    <>
      <section className="container page-head">
        <p className="eyebrow">Order for pickup</p>
        <h1 ref={heading} tabIndex={-1}>
          Our menu
        </h1>
        <p className="lead">
          Everything is cooked to order. Choose a dish to pick its size, how hot you want it and any
          extras.
        </p>
      </section>

      <section className="container menu-tools" aria-label="Find a dish">
        <div className="search-field">
          <label htmlFor="menu-search" className="visually-hidden">
            Search the menu
          </label>
          <Icon name="search" />
          <input
            id="menu-search"
            className="input"
            type="search"
            placeholder="Search dishes or ingredients"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <div className="tabs" role="tablist" aria-label="Menu sections">
          {tabs.map((item, index) => (
            <button
              key={item.id}
              ref={(node) => {
                tabRefs.current[index] = node
              }}
              type="button"
              role="tab"
              className="tab"
              id={`tab-${item.id}`}
              aria-selected={tab === item.id}
              aria-controls="menu-panel"
              tabIndex={tab === item.id ? 0 : -1}
              onClick={() => setTab(item.id)}
              onKeyDown={(event) => onTabKey(event, index)}
            >
              {item.name}
            </button>
          ))}
        </div>
      </section>

      <section
        className="container menu-panel"
        id="menu-panel"
        role="tabpanel"
        aria-labelledby={`tab-${tab}`}
      >
        <p className="menu-count" role="status">
          {shown.length === 1 ? '1 dish' : `${shown.length} dishes`}
          {query.trim() ? ` match “${query.trim()}”` : ''}
        </p>
        {groups.map(({ category, items }) => (
          <div className="menu-group" key={category.id}>
            <h2>{category.name}</h2>
            <p className="muted">{category.blurb}</p>
            <ul className="card-grid">
              {items.map((dish) => (
                <DishCard key={dish.slug} dish={dish} />
              ))}
            </ul>
          </div>
        ))}
        {!shown.length && (
          <div className="empty-state">
            <h2>No dishes found</h2>
            <p>Try a different word, such as “lamb”, “paneer” or “mango”, or clear the search.</p>
            <button type="button" className="btn btn--secondary" onClick={() => setQuery('')}>
              Clear the search
            </button>
          </div>
        )}
      </section>
      {dish && <DishDialog key={dish.slug} dish={dish} onClose={() => navigate('/menu')} />}
    </>
  )
}
