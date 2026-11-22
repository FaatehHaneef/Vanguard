// Reservations are kept in this browser tab only; nothing is sent anywhere.
const KEY = 'northgate.reservation'

// The same card and book always give the same reservation number.
function reservationNumber(card, bookId) {
  let hash = 7
  for (const char of `${card}:${bookId}`) hash = (hash * 31 + char.charCodeAt(0)) % 100000000
  return String(hash).padStart(8, '0').replace(/(\d{4})(\d{4})/, '$1 $2')
}

// `card` is null for a staff reservation made with the shortcut code.
export function saveReservation(book, card, name) {
  const reservation = {
    number: reservationNumber(card ?? 'staff', book.id),
    title: book.title,
    author: book.author,
    ready: book.available > 0,
    cardEnd: card ? card.slice(-4) : null,
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
