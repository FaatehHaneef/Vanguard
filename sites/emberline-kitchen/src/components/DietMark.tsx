import type { Diet } from '../data/menu'
import { Icon } from './Icon'

/** The leaf mark: dark green for vegan dishes, light green for vegetarian ones. */
export function DietMark({ diet }: { diet?: Diet }) {
  if (!diet) return null
  return (
    <span className={`diet-mark diet-mark--${diet}`}>
      <Icon name="leaf" />
    </span>
  )
}

export function DietLegend() {
  return (
    <p className="diet-legend">
      <span>
        <span className="diet-swatch diet-swatch--vegan" aria-hidden="true" /> Vegan
      </span>
      <span>
        <span className="diet-swatch diet-swatch--vegetarian" aria-hidden="true" /> Vegetarian
      </span>
    </p>
  )
}
