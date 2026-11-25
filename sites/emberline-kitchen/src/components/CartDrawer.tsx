import { useRef } from 'react'
import { Link } from 'react-router'
import { formatPrice } from '../data/menu'
import { lineExtras, lineTitle, MAX_QUANTITY, useCart } from '../lib/cart'
import { useFocusTrap } from '../lib/focus'
import { Icon } from './Icon'

export function CartDrawer() {
  const cart = useCart()
  const drawer = useRef<HTMLDivElement>(null)
  const close = cart.closeDrawer

  useFocusTrap(drawer, cart.drawerOpen, close)

  if (!cart.drawerOpen) return null
  return (
    <>
      <div className="drawer-overlay" onMouseDown={close} />
      <div
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="order-title"
        ref={drawer}
        tabIndex={-1}
      >
        <div className="drawer-head">
          <h2 id="order-title">Your order</h2>
          <button type="button" className="icon-btn" aria-label="Close" onClick={close}>
            <Icon name="close" />
          </button>
        </div>
        <div className="drawer-body">
          {cart.lines.length ? (
            <ul className="order-lines">
              {cart.lines.map((line) => {
                const title = lineTitle(line)
                const extras = lineExtras(line)
                return (
                  <li className="order-line" key={line.key}>
                    <div className="order-line__text">
                      <p className="order-line__title">{title}</p>
                      {extras && <p className="order-line__extras">{extras}</p>}
                      <p className="order-line__price">{formatPrice(line.unitPrice * line.quantity)}</p>
                    </div>
                    <div className="order-line__controls">
                      <div className="quantity" role="group" aria-label={`Quantity of ${title}`}>
                        <button
                          type="button"
                          className="icon-btn"
                          aria-label="One fewer"
                          onClick={() => cart.setQuantity(line.key, line.quantity - 1)}
                        >
                          <Icon name="minus" />
                        </button>
                        <output>{line.quantity}</output>
                        <button
                          type="button"
                          className="icon-btn"
                          aria-label="One more"
                          disabled={line.quantity >= MAX_QUANTITY}
                          onClick={() => cart.setQuantity(line.key, line.quantity + 1)}
                        >
                          <Icon name="plus" />
                        </button>
                      </div>
                      <button
                        type="button"
                        className="btn btn--ghost btn--sm"
                        onClick={() => cart.remove(line.key)}
                      >
                        Remove
                      </button>
                    </div>
                  </li>
                )
              })}
            </ul>
          ) : (
            <div className="order-empty">
              <p>Your order is empty. Choose a dish from the menu to get started.</p>
              <Link to="/menu" className="btn btn--secondary btn--sm" onClick={close}>
                Browse the menu
              </Link>
            </div>
          )}
        </div>
        {!!cart.lines.length && (
          <div className="drawer-foot">
            <p className="order-total">
              <span>Subtotal</span>
              <strong>{formatPrice(cart.subtotal)}</strong>
            </p>
            <Link to="/checkout" className="btn btn--primary btn--block" onClick={close}>
              Go to checkout
            </Link>
            <button type="button" className="btn btn--ghost btn--block" onClick={close}>
              Keep browsing
            </button>
          </div>
        )}
      </div>
    </>
  )
}
