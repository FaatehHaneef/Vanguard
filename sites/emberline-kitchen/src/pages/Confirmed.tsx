import { Link } from 'react-router'
import { formatPrice } from '../data/menu'
import { lastOrder } from '../lib/order'
import { usePage } from '../lib/page'
import { CheckoutSteps } from './Checkout'

export function Confirmed() {
  const order = lastOrder()
  const heading = usePage(order ? 'Order placed' : 'No recent order')

  if (!order) {
    return (
      <section className="container page-head">
        <h1 ref={heading} tabIndex={-1}>
          We could not find a recent order
        </h1>
        <p className="lead">Orders placed in this browser tab show up here. Start a new one from the menu.</p>
        <Link to="/menu" className="btn btn--primary">
          Browse the menu
        </Link>
      </section>
    )
  }

  const firstName = order.name.split(/\s+/)[0]
  return (
    <section className="container confirmed">
      <div className="page-head">
        <CheckoutSteps current={3} />
        <p className="eyebrow">Order {order.number}</p>
        <h1 ref={heading} tabIndex={-1}>
          Thank you, {firstName}
        </h1>
        <p className="lead">
          Your order will be ready for pickup at {order.time}. Give the name {order.name} or order
          number {order.number} at the counter.
        </p>
      </div>

      <div className="confirmed__layout">
        <div className="panel">
          <h2>What you ordered</h2>
          <ul className="order-lines">
            {order.lines.map((line, index) => (
              <li className="order-line order-line--compact" key={index}>
                <div className="order-line__text">
                  <p className="order-line__title">
                    {line.quantity} × {line.title}
                  </p>
                  {line.extras && <p className="order-line__extras">{line.extras}</p>}
                </div>
                <span className="order-line__price">{formatPrice(line.price)}</span>
              </li>
            ))}
          </ul>
          {order.discount > 0 && (
            <p className="order-total order-total--minor">
              <span>Discount</span>
              <span>−{formatPrice(order.discount)}</span>
            </p>
          )}
          <p className="order-total">
            <span>To pay at the counter</span>
            <strong>{formatPrice(order.total)}</strong>
          </p>
          {order.notes && (
            <p className="muted">
              <strong>Your note:</strong> {order.notes}
            </p>
          )}
        </div>
        <div className="panel confirmed__where">
          <h2>Where to collect</h2>
          <p>
            Emberline Kitchen
            <br />
            14 Copper Street, Harwick HW2 4LT
          </p>
          <p>
            If you are running late, call us on 01632 960214 and we will keep your food warm.
          </p>
          <Link to="/menu" className="btn btn--secondary">
            Back to the menu
          </Link>
        </div>
      </div>
    </section>
  )
}
