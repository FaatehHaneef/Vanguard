type IconName =
  | 'bag'
  | 'search'
  | 'close'
  | 'chevron-down'
  | 'arrow-left'
  | 'arrow-right'
  | 'minus'
  | 'plus'
  | 'flame'
  | 'leaf'
  | 'clock'
  | 'pin'
  | 'phone'
  | 'menu'
  | 'check'
  | 'trash'

const paths: Record<IconName, string> = {
  bag: 'M6 8h12l-1 12H7L6 8zm3 0V6a3 3 0 0 1 6 0v2',
  search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm9 16-4.3-4.3',
  close: 'M6 6l12 12M18 6 6 18',
  'chevron-down': 'M6 9l6 6 6-6',
  'arrow-left': 'M15 5l-7 7 7 7',
  'arrow-right': 'M9 5l7 7-7 7',
  minus: 'M5 12h14',
  plus: 'M12 5v14M5 12h14',
  flame: 'M12 3c2.5 3.5 6 6 6 11a6 6 0 0 1-12 0c0-2.6 1.3-4.4 2.6-5.6.3 1.8 1 3 2.2 3.5C10.6 9.2 11 6 12 3z',
  leaf: 'M5 19c0-8 5-13 14-14 0 9-5 14-13 14m0 0c2-4 5-7 9-9',
  clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 4v5l3 2',
  pin: 'M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21zm0-9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
  phone: 'M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2',
  menu: 'M4 7h16M4 12h16M4 17h16',
  check: 'M5 12.5l4.5 4.5L19 7',
  trash: 'M5 7h14M10 7V5h4v2m-7 0 1 13h8l1-13',
}

export function Icon({ name, className }: { name: IconName; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d={paths[name]} />
    </svg>
  )
}
