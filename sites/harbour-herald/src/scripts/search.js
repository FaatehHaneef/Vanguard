// Search: every word of the query must appear in the story (case and accents ignored).
// Results are ranked by how many query words appear in the headline, then by date order.
const normalise = (text) =>
  text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9£]+/g, " ")
    .trim();

export function search(index, query) {
  const words = normalise(query).split(" ").filter(Boolean);
  if (words.length === 0) return [];
  return index
    .map((item, order) => ({ item, order, text: normalise(item.text), title: normalise(item.title) }))
    .filter(({ text }) => words.every((word) => text.includes(word)))
    .map((entry) => ({ ...entry, score: words.filter((word) => entry.title.includes(word)).length }))
    .sort((a, b) => b.score - a.score || a.order - b.order)
    .map(({ item }) => item);
}
