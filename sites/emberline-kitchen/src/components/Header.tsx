import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router'
import { Icon } from './Icon'
import { Logo } from './Logo'

const links = [
  { to: '/menu', label: 'Menu' },
  { to: '/hours', label: 'Hours & location' },
  { to: '/about', label: 'About us' },
]

export function Header() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => setOpen(false), [location.pathname])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => event.key === 'Escape' && setOpen(false)
    const onClick = (event: MouseEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('mousedown', onClick)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('mousedown', onClick)
    }
  }, [open])

  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <Link to="/" className="brand">
          <Logo />
          <span>Emberline Kitchen</span>
        </Link>
        <nav aria-label="Main" className="site-nav">
          <ul>
            {links.map((link) => (
              <li key={link.to}>
                <NavLink to={link.to}>{link.label}</NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="site-header__actions">
          <Link to="/menu" className="btn btn--primary btn--sm header-cta">
            Order for pickup
          </Link>
          <div className="dropdown site-nav-mobile" ref={menuRef}>
            <button
              type="button"
              className="icon-btn"
              aria-expanded={open}
              aria-controls="mobile-nav"
              aria-label="Site menu"
              onClick={() => setOpen((value) => !value)}
            >
              <Icon name={open ? 'close' : 'menu'} />
            </button>
            {open && (
              <ul className="dropdown-panel" id="mobile-nav">
                {links.map((link) => (
                  <li key={link.to}>
                    <Link to={link.to}>{link.label}</Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
