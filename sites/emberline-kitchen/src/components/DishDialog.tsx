import { useId, useRef, useState } from 'react'
import { DEFAULT_SPICE, type Dish, formatPrice, sizes, type SizeId, spiceLevels } from '../data/menu'
import { MAX_QUANTITY, useCart } from '../lib/cart'
import { useFocusTrap } from '../lib/focus'
import { DietMark } from './DietMark'
import { DishArt } from './DishArt'
import { Icon } from './Icon'

interface Props {
  dish: Dish
  onClose: () => void
}

export function DishDialog({ dish, onClose }: Props) {
  const cart = useCart()
  const titleId = useId()
  const dialog = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState<SizeId>('regular')
  const [extras, setExtras] = useState<string[]>([])
  const [spice, setSpice] = useState<string>(DEFAULT_SPICE)
  const [spiceOpen, setSpiceOpen] = useState(false)
  const [quantity, setQuantity] = useState(1)

  useFocusTrap(dialog, true, onClose, () =>
    document.querySelector<HTMLElement>(`a[href="/menu/${dish.slug}"]`),
  )

  const surcharge = dish.sizes ? (sizes.find((s) => s.id === size)?.surcharge ?? 0) : 0
  const extrasPrice = (dish.extras ?? [])
    .filter((extra) => extras.includes(extra.id))
    .reduce((sum, extra) => sum + extra.price, 0)
  const unitPrice = dish.price + surcharge + extrasPrice

  const toggleExtra = (id: string) =>
    setExtras((current) => (current.includes(id) ? current.filter((x) => x !== id) : [...current, id]))

  const addToOrder = () => {
    cart.add({
      slug: dish.slug,
      size: dish.sizes ? size : undefined,
      spice: dish.spicy ? spice : undefined,
      extras,
      quantity,
      unitPrice,
    })
    onClose()
    cart.openDrawer()
  }

  return (
    <div
      className="overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div
        className="dialog dish-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        ref={dialog}
        tabIndex={-1}
      >
        <button type="button" className="icon-btn dialog-close" aria-label="Close" onClick={onClose}>
          <Icon name="close" />
        </button>
        <DishArt category={dish.category} hue={dish.hue} />
        <div className="dish-dialog__body">
          <h2 id={titleId} className="dish-dialog__title">
            {dish.name}
          </h2>
          <p className="dish-dialog__price">
            {formatPrice(dish.price)} <DietMark diet={dish.diet} />
          </p>
          <p>{dish.description}</p>
          {(dish.glutenFree || dish.containsNuts) && (
            <p className="dish-dialog__badges">
              {dish.glutenFree && <span className="badge">Gluten free</span>}
              {dish.containsNuts && <span className="badge">Contains nuts</span>}
            </p>
          )}

          {dish.sizes && (
            <fieldset className="field">
              <legend>Size</legend>
              <div className="options">
                {sizes.map((option) => (
                  <label className="option" key={option.id}>
                    <input
                      type="radio"
                      name="size"
                      value={option.id}
                      checked={size === option.id}
                      onChange={() => setSize(option.id)}
                    />
                    <span>
                      {option.name}
                      <small>{formatPrice(dish.price + option.surcharge)}</small>
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>
          )}

          {dish.spicy && (
            <div className="field">
              <span className="field-label">Spice level</span>
              <div className="spice-select">
                <div
                  className={`spice-select__value${spiceOpen ? ' is-open' : ''}`}
                  onClick={() => setSpiceOpen((value) => !value)}
                >
                  <span className="spice-select__heat" data-level={spiceLevels.indexOf(spice as never)}>
                    <Icon name="flame" />
                  </span>
                  <span>{spice}</span>
                  <Icon name="chevron-down" className="spice-select__chevron" />
                </div>
                {spiceOpen && (
                  <div className="spice-select__list">
                    {spiceLevels.map((level) => (
                      <div
                        key={level}
                        className={`spice-select__option${level === spice ? ' is-selected' : ''}`}
                        onClick={() => {
                          setSpice(level)
                          setSpiceOpen(false)
                        }}
                      >
                        {level}
                        {level === spice && <Icon name="check" />}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {!!dish.extras?.length && (
            <fieldset className="field">
              <legend>Extras</legend>
              <div className="options">
                {dish.extras.map((extra) => (
                  <label className="option" key={extra.id}>
                    <input
                      type="checkbox"
                      checked={extras.includes(extra.id)}
                      onChange={() => toggleExtra(extra.id)}
                    />
                    <span>
                      {extra.name}
                      <small>+{formatPrice(extra.price)}</small>
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>
          )}

          <div className="field">
            <span className="field-label" id={`${titleId}-qty`}>
              Quantity
            </span>
            <div className="quantity" role="group" aria-labelledby={`${titleId}-qty`}>
              <button
                type="button"
                className="icon-btn"
                aria-label="One fewer"
                disabled={quantity <= 1}
                onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              >
                <Icon name="minus" />
              </button>
              <output aria-live="polite">{quantity}</output>
              <button
                type="button"
                className="icon-btn"
                aria-label="One more"
                disabled={quantity >= MAX_QUANTITY}
                onClick={() => setQuantity((q) => Math.min(MAX_QUANTITY, q + 1))}
              >
                <Icon name="plus" />
              </button>
            </div>
          </div>
        </div>
        <div className="dish-dialog__foot">
          <button type="button" className="btn btn--primary btn--block" onClick={addToOrder}>
            Add to order · {formatPrice(unitPrice * quantity)}
          </button>
        </div>
      </div>
    </div>
  )
}
