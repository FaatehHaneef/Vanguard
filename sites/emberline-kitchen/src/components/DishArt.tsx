import type { CategoryId } from '../data/menu'

/** A small illustration of a dish, drawn from its category and colour. */
export function DishArt({ category, hue }: { category: CategoryId; hue: number }) {
  const main = `hsl(${hue} 70% 46%)`
  const light = `hsl(${hue} 80% 68%)`
  const back = `hsl(${hue} 60% 92%)`
  return (
    <svg className="dish-art" viewBox="0 0 160 110" aria-hidden="true" focusable="false">
      <rect width="160" height="110" fill={back} />
      <circle cx="132" cy="18" r="30" fill={light} opacity="0.35" />
      {category === 'curries' && (
        <g>
          <ellipse cx="80" cy="74" rx="52" ry="16" fill="#2a1d17" opacity="0.15" />
          <path d="M30 56h100a50 24 0 0 1-100 0z" fill="#3d2c24" />
          <ellipse cx="80" cy="56" rx="50" ry="12" fill={main} />
          <circle cx="66" cy="54" r="5" fill={light} />
          <circle cx="90" cy="58" r="4" fill={light} />
          <path
            d="M72 50c3-4 8-4 10 0M96 52c2-3 6-3 8 0"
            stroke="#4c9a57"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M60 36c-4-6 4-8 0-14M80 34c-4-6 4-8 0-14M100 36c-4-6 4-8 0-14"
            stroke="#a8988e"
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
            opacity="0.7"
          />
        </g>
      )}
      {category === 'grill' && (
        <g>
          <ellipse cx="80" cy="82" rx="58" ry="10" fill="#2a1d17" opacity="0.15" />
          <rect x="18" y="56" width="124" height="5" rx="2.5" fill="#6b5a51" />
          {[36, 58, 80, 102, 124].map((x, index) => (
            <rect key={x} x={x - 9} y="46" width="18" height="24" rx="7" fill={index % 2 ? light : main} />
          ))}
          <path
            d="M40 92c6-10 14-10 20 0M76 92c6-10 14-10 20 0M110 92c6-10 14-10 20 0"
            stroke="#f08a24"
            strokeWidth="4"
            fill="none"
            strokeLinecap="round"
          />
        </g>
      )}
      {category === 'small-plates' && (
        <g>
          <ellipse cx="80" cy="80" rx="58" ry="14" fill="#2a1d17" opacity="0.12" />
          <ellipse cx="80" cy="70" rx="56" ry="16" fill="#fffaf3" stroke="#ead5b6" strokeWidth="3" />
          <path d="M52 70l14-24 14 24z" fill={main} />
          <path d="M76 72l14-26 14 26z" fill={light} />
          <path d="M98 70l12-20 12 20z" fill={main} />
          <circle cx="44" cy="68" r="7" fill="#4c9a57" />
        </g>
      )}
      {category === 'rice-bread' && (
        <g>
          <ellipse cx="80" cy="84" rx="58" ry="10" fill="#2a1d17" opacity="0.12" />
          <path d="M26 64c10-30 46-34 62-10 6 10 0 26-20 28-24 2-48-2-42-18z" fill={light} />
          <circle cx="44" cy="62" r="3" fill={main} />
          <circle cx="60" cy="56" r="3" fill={main} />
          <circle cx="54" cy="70" r="3" fill={main} />
          <path d="M92 68h48a24 14 0 0 1-48 0z" fill="#3d2c24" />
          <ellipse cx="116" cy="66" rx="24" ry="8" fill="#fff1d1" />
          <circle cx="110" cy="62" r="3" fill={main} />
        </g>
      )}
      {category === 'sweets' && (
        <g>
          <ellipse cx="80" cy="88" rx="50" ry="8" fill="#2a1d17" opacity="0.12" />
          <path d="M44 30h28l-4 56H48z" fill="#fffaf3" stroke="#ead5b6" strokeWidth="3" />
          <path d="M46 44h24l-3 40H49z" fill={main} />
          <path d="M92 64h48a24 18 0 0 1-48 0z" fill="#fffaf3" stroke="#ead5b6" strokeWidth="3" />
          <circle cx="106" cy="60" r="9" fill={light} />
          <circle cx="124" cy="60" r="9" fill={main} />
        </g>
      )}
    </svg>
  )
}
