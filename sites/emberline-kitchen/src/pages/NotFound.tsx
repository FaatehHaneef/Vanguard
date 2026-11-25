import { Link } from 'react-router'
import { usePage } from '../lib/page'

export function NotFound() {
  const heading = usePage('Page not found')
  return (
    <section className="container page-head">
      <p className="eyebrow">Error 404</p>
      <h1 ref={heading} tabIndex={-1}>
        We couldn’t find that page
      </h1>
      <p className="lead">The link may be out of date. Our menu and opening hours are a click away.</p>
      <p>
        <Link to="/menu" className="btn btn--primary">
          See the menu
        </Link>
      </p>
    </section>
  )
}
