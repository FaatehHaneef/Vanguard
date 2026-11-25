import { books } from './data/books.js'

// Each book's cover colour comes from its place in the catalogue, so it never changes.
const PALETTE = ['#1d4e5f', '#b04a4a', '#c8902e', '#4f8a5b', '#6a4c93', '#2f6f8f', '#8a5d12', '#3d5a40']

export function coverColour(book) {
  const index = books.findIndex((entry) => entry.id === book.id)
  return PALETTE[(index < 0 ? 0 : index) % PALETTE.length]
}
