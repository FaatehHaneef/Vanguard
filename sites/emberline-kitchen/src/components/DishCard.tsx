import { Link } from 'react-router'
import { type Dish, formatPrice } from '../data/menu'
import { DishArt } from './DishArt'

export function DishCard({ dish }: { dish: Dish }) {
  return (
    <li className="card dish-card">
      <DishArt category={dish.category} hue={dish.hue} />
      <div className="dish-card__body">
        <h3 className="dish-card__name">
          <Link to={`/menu/${dish.slug}`} className="dish-card__link">
            {dish.name}
          </Link>
        </h3>
        <p className="dish-card__desc">{dish.description}</p>
        <div className="dish-card__meta">
          <span className="dish-card__price">{formatPrice(dish.price)}</span>
          {dish.glutenFree && <span className="badge">Gluten free</span>}
          {dish.containsNuts && <span className="badge">Contains nuts</span>}
        </div>
      </div>
    </li>
  )
}
