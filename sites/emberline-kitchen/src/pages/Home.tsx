import { Link } from 'react-router'
import { usePage } from '../lib/page'

export function Home() {
  const heading = usePage('')
  return (
    <section className="container page-head">
      <p className="eyebrow">Copper Street, Harwick</p>
      <h1 ref={heading} tabIndex={-1}>
        Cooked over coals, ready when you are
      </h1>
      <p className="lead">Order online and collect from our counter.</p>
      <Link to="/menu" className="btn btn--primary">
        Order for pickup
      </Link>
    </section>
  )
}
