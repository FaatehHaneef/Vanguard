// Reservations are kept in this browser tab only; nothing is sent anywhere.
const KEY = 'northgate.reservation'

// The same card and book always give the same reservation number.
function reservationNumber(card, bookId) {
  let hash = 7
  for (const char of `${card}:${bookId}`) hash = (hash * 31 + char.charCodeAt(0)) % 100000000
  return String(hash).padStart(8, '0').replace(/(\d{4})(\d{4})/, '$1 $2')
}

export function saveReservation(book, card, name) {
  const reservation = {
    number: reservationNumber(card, book.id),
    title: book.title,
    author: book.author,
    ready: book.available > 0,
    cardEnd: card.slice(-4),
    name,
  }
  sessionStorage.setItem(KEY, JSON.stringify(reservation))
}

export function loadReservation() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY))
  } catch {
    return null
  }
}
