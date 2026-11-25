/** The collection ticket shown after an order: a picture for the counter screen. */
export function Ticket({ number, time }: { number: string; time: string }) {
  const bars = [3, 1, 2, 1, 3, 2, 1, 1, 3, 1, 2, 3, 1, 2, 1, 3, 1, 1, 2, 3, 1, 2, 2, 1, 3, 1]
  let x = 24
  return (
    <svg className="ticket" viewBox="0 0 320 180" aria-hidden="true" focusable="false">
      <path
        d="M12 0h296a12 12 0 0 0 12 12v52a14 14 0 0 0 0 28v76a12 12 0 0 0-12 12H12a12 12 0 0 0-12-12V92a14 14 0 0 0 0-28V12A12 12 0 0 0 12 0z"
        fill="#2a1d17"
      />
      <text x="24" y="34" fill="#ffd27a" fontSize="12" fontFamily="sans-serif" letterSpacing="2">
        COLLECTION
      </text>
      <text x="24" y="64" fill="#fffaf3" fontSize="26" fontFamily="serif" fontWeight="700">
        No. {number}
      </text>
      <text x="296" y="64" fill="#fffaf3" fontSize="20" fontFamily="sans-serif" textAnchor="end">
        {time}
      </text>
      <line x1="20" y1="78" x2="300" y2="78" stroke="#6b5a51" strokeDasharray="4 5" />
      {bars.map((width, index) => {
        const bar = <rect key={index} x={x} y="94" width={width * 2} height="48" fill="#fffaf3" />
        x += width * 2 + 3
        return bar
      })}
      <text x="24" y="162" fill="#a8988e" fontSize="12" fontFamily="monospace" letterSpacing="1">
        EB-4417
      </text>
      <text x="296" y="162" fill="#a8988e" fontSize="12" fontFamily="sans-serif" textAnchor="end">
        Emberline Kitchen
      </text>
    </svg>
  )
}
