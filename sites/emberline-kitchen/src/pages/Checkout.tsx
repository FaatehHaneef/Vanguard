import { type FormEvent, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { formatPrice } from '../data/menu'
import { lineExtras, lineTitle, useCart } from '../lib/cart'
import {
  parseTime,
  PICKUP_CLOSES,
  PICKUP_OPENS,
  placeOrder,
  validPhone,
  withinPickupHours,
} from '../lib/order'
import { usePage } from '../lib/page'

type Field = 'name' | 'phone' | 'time' | 'promo'
type Errors = Partial<Record<Field, string>>

const PLACING_DELAY_MS = 250

export function CheckoutSteps({ current }: { current: 1 | 2 | 3 }) {
  const steps = ['Choose dishes', 'Your details', 'Confirmed']
  return (
    <ol className="stepper" aria-label="Order progress">
      {steps.map((step, index) => (
        <li
          key={step}
          className={index + 1 < current ? 'is-done' : undefined}
          aria-current={index + 1 === current ? 'step' : undefined}
        >
          {step}
        </li>
      ))}
    </ol>
  )
}

export function Checkout() {
  const heading = usePage('Checkout')
  const cart = useCart()
  const navigate = useNavigate()
  const [values, setValues] = useState({ name: '', phone: '', time: '', notes: '', promo: '' })
  const [errors, setErrors] = useState<Errors>({})
  const [placing, setPlacing] = useState(false)
  const refs = {
    name: useRef<HTMLInputElement>(null),
    phone: useRef<HTMLInputElement>(null),
    time: useRef<HTMLInputElement>(null),
    promo: useRef<HTMLInputElement>(null),
  }

  const update = (field: keyof typeof values) => (event: { target: { value: string } }) =>
    setValues((current) => ({ ...current, [field]: event.target.value }))

  const validate = (): Errors => {
    const found: Errors = {}
    if (!values.name.trim()) found.name = 'Enter the name we should call out at the counter.'
    if (!values.phone.trim()) found.phone = 'Enter a phone number so that we can reach you.'
    else if (!validPhone(values.phone))
      found.phone = 'Enter a UK phone number, for example 07700 900123.'
    const time = parseTime(values.time)
    if (!values.time.trim()) found.time = 'Enter the time you would like to collect your order.'
    else if (!time)
      found.time = 'Enter the time as hours and minutes on the 24-hour clock, for example 18:30.'
    else if (!withinPickupHours(time))
      found.time = `We take pickup orders from ${PICKUP_OPENS} to ${PICKUP_CLOSES}. Please choose a time in that window.`
    if (values.promo.trim()) found.promo = 'That code is not valid. Check it and try again, or leave the box empty.'
    return found
  }

  const submit = (event: FormEvent) => {
    event.preventDefault()
    if (placing) return
    const found = validate()
    setErrors(found)
    const first = (['name', 'phone', 'time', 'promo'] as Field[]).find((field) => found[field])
    if (first) {
      refs[first].current?.focus()
      return
    }
    setPlacing(true)
    const order = placeOrder(
      {
        name: values.name.trim(),
        phone: values.phone.trim(),
        time: parseTime(values.time)!,
        notes: values.notes.trim(),
      },
      cart.lines,
      0,
    )
    window.setTimeout(() => {
      cart.clear()
      navigate(`/order/confirmed?number=${order.number}`)
    }, PLACING_DELAY_MS)
  }

  if (!cart.lines.length) {
    return (
      <section className="container page-head">
        <CheckoutSteps current={1} />
        <h1 ref={heading} tabIndex={-1}>
          Your order is empty
        </h1>
        <p className="lead">Choose something from the menu first, then come back here to check out.</p>
        <Link to="/menu" className="btn btn--primary">
          Browse the menu
        </Link>
      </section>
    )
  }

  const describedBy = (field: Field, hint?: string) =>
    [hint, errors[field] ? `${field}-error` : ''].filter(Boolean).join(' ') || undefined

  return (
    <section className="container checkout">
      <div className="page-head">
        <CheckoutSteps current={2} />
        <h1 ref={heading} tabIndex={-1}>
          Checkout
        </h1>
        <p className="lead">Tell us who is collecting and when. You pay at the counter.</p>
      </div>

      <div className="checkout__layout">
        <form className="panel checkout__form" noValidate onSubmit={submit}>
          <h2>Pickup details</h2>
          <div className="field">
            <label htmlFor="name">Name for the order</label>
            <input
              id="name"
              ref={refs.name}
              className="input"
              autoComplete="name"
              value={values.name}
              onChange={update('name')}
              aria-invalid={Boolean(errors.name)}
              aria-describedby={describedBy('name')}
            />
            {errors.name && (
              <p className="field-error" id="name-error">
                {errors.name}
              </p>
            )}
          </div>
          <div className="field">
            <label htmlFor="phone">Phone number</label>
            <p className="hint" id="phone-hint">
              We only call if there is a problem with your order.
            </p>
            <input
              id="phone"
              ref={refs.phone}
              className="input"
              type="tel"
              autoComplete="tel"
              value={values.phone}
              onChange={update('phone')}
              aria-invalid={Boolean(errors.phone)}
              aria-describedby={describedBy('phone', 'phone-hint')}
            />
            {errors.phone && (
              <p className="field-error" id="phone-error">
                {errors.phone}
              </p>
            )}
          </div>
          <div className="field">
            <label htmlFor="time">Pickup time today</label>
            <p className="hint" id="time-hint">
              Use the 24-hour clock, for example 18:30.
            </p>
            <input
              id="time"
              ref={refs.time}
              className="input input--short"
              inputMode="numeric"
              value={values.time}
              onChange={update('time')}
              aria-invalid={Boolean(errors.time)}
              aria-describedby={describedBy('time', 'time-hint')}
            />
            {errors.time && (
              <p className="field-error" id="time-error">
                {errors.time}
              </p>
            )}
          </div>
          <div className="field">
            <label htmlFor="notes">Notes for the kitchen (optional)</label>
            <textarea
              id="notes"
              className="textarea"
              value={values.notes}
              onChange={update('notes')}
            />
          </div>
          <div className="field">
            <label htmlFor="promo">Promo code (optional)</label>
            <input
              id="promo"
              ref={refs.promo}
              className="input input--short"
              autoComplete="off"
              value={values.promo}
              onChange={update('promo')}
              aria-invalid={Boolean(errors.promo)}
              aria-describedby={describedBy('promo')}
            />
            {errors.promo && (
              <p className="field-error" id="promo-error">
                {errors.promo}
              </p>
            )}
          </div>
          <button type="submit" className="btn btn--primary btn--block" disabled={placing}>
            {placing ? 'Placing your order…' : 'Place order'}
          </button>
        </form>

        <aside className="panel checkout__summary" aria-labelledby="summary-title">
          <h2 id="summary-title">Order summary</h2>
          <ul className="order-lines">
            {cart.lines.map((line) => (
              <li className="order-line order-line--compact" key={line.key}>
                <div className="order-line__text">
                  <p className="order-line__title">
                    {line.quantity} × {lineTitle(line)}
                  </p>
                  {lineExtras(line) && <p className="order-line__extras">{lineExtras(line)}</p>}
                </div>
                <span className="order-line__price">{formatPrice(line.unitPrice * line.quantity)}</span>
              </li>
            ))}
          </ul>
          <p className="order-total">
            <span>Total to pay at pickup</span>
            <strong>{formatPrice(cart.subtotal)}</strong>
          </p>
          <button type="button" className="btn btn--ghost btn--sm" onClick={cart.openDrawer}>
            Change your order
          </button>
        </aside>
      </div>
    </section>
  )
}
