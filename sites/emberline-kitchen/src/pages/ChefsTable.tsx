import { Link } from 'react-router'
import { usePage } from '../lib/page'

export function ChefsTable() {
  const heading = usePage('Chef’s table')
  return (
    <>
      <section className="container page-head chefs-head">
        <p className="eyebrow">For our chef’s table guests</p>
        <h1 ref={heading} tabIndex={-1}>
          Thank you for joining us at the pass
        </h1>
        <p className="lead">
          Once a month Rukhsana cooks a seven-course tasting menu for eight guests at the counter.
          This page is for the people who have sat with us.
        </p>
      </section>
      <section className="container chefs-layout">
        <div className="panel">
          <h2>Your guest code</h2>
          <p>
            As a thank-you, enter this code in the promo code box at checkout and we will take £5.00
            off your next pickup order:
          </p>
          <p className="guest-code">EC-2690</p>
          <p className="muted">One use per order. It works on any pickup order, with no minimum spend.</p>
          <Link to="/menu" className="btn btn--primary">
            Start an order
          </Link>
        </div>
        <div className="panel">
          <h2>Next tasting evenings</h2>
          <ul className="tasting-list">
            <li>
              <strong>Thursday 3 December</strong> Winter in Kashmir: rogan josh, haak and kahwa
            </li>
            <li>
              <strong>Thursday 7 January</strong> Lahore street food, from chaat to nihari
            </li>
            <li>
              <strong>Thursday 4 February</strong> The tandoor, course by course
            </li>
          </ul>
          <p className="muted">To book a seat, ask at the counter or call 01632 960214.</p>
        </div>
      </section>
    </>
  )
}
