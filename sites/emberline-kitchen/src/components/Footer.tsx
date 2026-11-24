import { Link } from 'react-router'
import { Logo } from './Logo'

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer__grid">
        <div>
          <Link to="/" className="brand brand--light">
            <Logo />
            <span>Emberline Kitchen</span>
          </Link>
          <p className="site-footer__blurb">
            Punjabi and Kashmiri cooking from the coals. Order online, then collect from our
            counter on Copper Street.
          </p>
        </div>
        <div>
          <h2 className="site-footer__title">Visit</h2>
          <p>
            14 Copper Street
            <br />
            Harwick HW2 4LT
            <br />
            01632 960214
          </p>
        </div>
        <div>
          <h2 className="site-footer__title">Pickup hours</h2>
          <p>
            Tuesday to Sunday
            <br />
            12:00 to 21:30
            <br />
            Closed on Mondays
          </p>
        </div>
        <nav aria-label="Footer">
          <h2 className="site-footer__title">Explore</h2>
          <ul>
            <li>
              <Link to="/menu">Menu</Link>
            </li>
            <li>
              <Link to="/hours">Hours & location</Link>
            </li>
            <li>
              <Link to="/about">About us</Link>
            </li>
            <li>
              <Link to="/about#questions">Questions</Link>
            </li>
          </ul>
        </nav>
      </div>
      <div className="container site-footer__base">
        <p>© 2026 Emberline Kitchen Ltd. Prices include VAT. Pay at the counter when you collect.</p>
        <p className="site-footer__reg">Food business registration EF-8053 · Hygiene rating 5</p>
      </div>
    </footer>
  )
}
