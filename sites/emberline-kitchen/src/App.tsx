import { useEffect, useRef } from 'react'
import { Route, Routes, useLocation } from 'react-router'
import { CartDrawer } from './components/CartDrawer'
import { Footer } from './components/Footer'
import { Header } from './components/Header'
import { About } from './pages/About'
import { Checkout } from './pages/Checkout'
import { Confirmed } from './pages/Confirmed'
import { Home } from './pages/Home'
import { Hours } from './pages/Hours'
import { Menu } from './pages/Menu'
import { NotFound } from './pages/NotFound'

function ScrollToTop() {
  const { pathname } = useLocation()
  const previous = useRef(pathname)
  useEffect(() => {
    const withinMenu = previous.current.startsWith('/menu') && pathname.startsWith('/menu')
    previous.current = pathname
    if (!withinMenu) window.scrollTo(0, 0)
  }, [pathname])
  return null
}

export function App() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <ScrollToTop />
      <Header />
      <main id="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/menu/:slug?" element={<Menu />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/order/confirmed" element={<Confirmed />} />
          <Route path="/hours" element={<Hours />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
      <CartDrawer />
    </>
  )
}
