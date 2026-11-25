export type CategoryId = 'small-plates' | 'curries' | 'grill' | 'rice-bread' | 'sweets'
export type Diet = 'vegan' | 'vegetarian'

export interface Extra {
  id: string
  name: string
  price: number // pence
}

export interface Dish {
  slug: string
  name: string
  category: CategoryId
  price: number // pence, regular size
  description: string
  diet?: Diet
  glutenFree?: boolean
  containsNuts?: boolean
  spicy?: boolean // cooked to a chosen spice level
  sizes?: boolean // offered in regular and large
  extras?: Extra[]
  featured?: boolean
  hue: number // colour of the dish illustration
}

export const categories: { id: CategoryId; name: string; blurb: string }[] = [
  { id: 'small-plates', name: 'Small plates', blurb: 'To share while the coals get going.' },
  { id: 'curries', name: 'Curries', blurb: 'Slow gravies and fast karahis, all cooked to order.' },
  { id: 'grill', name: 'From the grill', blurb: 'Marinated a day ahead and finished in the tandoor.' },
  { id: 'rice-bread', name: 'Rice & bread', blurb: 'Biryanis, plain rice and breads from the clay oven.' },
  { id: 'sweets', name: 'Desserts & drinks', blurb: 'Something cold, something sweet, something to sip.' },
]

export const LARGE_SURCHARGE = 300
export const sizes = [
  { id: 'regular', name: 'Regular', surcharge: 0 },
  { id: 'large', name: 'Large', surcharge: LARGE_SURCHARGE },
] as const
export type SizeId = (typeof sizes)[number]['id']

export const spiceLevels = ['Mild', 'Medium', 'Hot', 'Extra hot'] as const
export const DEFAULT_SPICE = 'Medium'

const raita: Extra = { id: 'raita', name: 'Cucumber raita', price: 125 }
const chilli: Extra = { id: 'green-chilli', name: 'Fried green chillies', price: 75 }
const onions: Extra = { id: 'onions', name: 'Pickled red onions', price: 95 }
const mintDip: Extra = { id: 'mint-dip', name: 'Mint yoghurt dip', price: 95 }
const butter: Extra = { id: 'butter', name: 'Brushed with butter', price: 50 }
const kulfi: Extra = { id: 'pistachio', name: 'Crushed pistachio', price: 60 }

export const dishes: Dish[] = [
  // Small plates
  {
    slug: 'vegetable-samosas',
    name: 'Vegetable Samosas',
    category: 'small-plates',
    price: 550,
    description:
      'Three crisp pastry parcels filled with spiced potato, peas and toasted cumin, served with our tamarind chutney.',
    diet: 'vegan',
    extras: [mintDip],
    hue: 32,
  },
  {
    slug: 'chilli-paneer',
    name: 'Chilli Paneer',
    category: 'small-plates',
    price: 725,
    description:
      'Cubes of fresh paneer tossed in the wok with peppers, spring onion and a sticky chilli glaze.',
    diet: 'vegetarian',
    spicy: true,
    hue: 8,
  },
  {
    slug: 'masala-fries',
    name: 'Masala Fries',
    category: 'small-plates',
    price: 475,
    description:
      'Hand-cut fries dusted with chaat masala and lime salt, with a garlic and coriander dip on the side.',
    diet: 'vegetarian',
    extras: [chilli],
    featured: true,
    hue: 42,
  },
  {
    slug: 'chicken-pakora',
    name: 'Chicken Pakora',
    category: 'small-plates',
    price: 650,
    description:
      'Strips of chicken thigh in a gram flour and ajwain batter, fried until golden and served with mint yoghurt.',
    glutenFree: true,
    spicy: true,
    hue: 26,
  },
  {
    slug: 'bhel-puri',
    name: 'Bhel Puri',
    category: 'small-plates',
    price: 525,
    description:
      'Puffed rice, crunchy sev, onion and tomato with tamarind and green chutneys, mixed to order so it stays crisp.',
    diet: 'vegan',
    hue: 50,
  },

  // Curries
  {
    slug: 'chicken-karahi',
    name: 'Chicken Karahi',
    category: 'curries',
    price: 1150,
    description:
      'Chicken on the bone cooked hard and fast in a karahi with tomato, ginger, green chilli and fresh coriander.',
    glutenFree: true,
    spicy: true,
    sizes: true,
    extras: [raita, chilli],
    featured: true,
    hue: 14,
  },
  {
    slug: 'lamb-rogan-josh',
    name: 'Lamb Rogan Josh',
    category: 'curries',
    price: 1325,
    description:
      'Slow-cooked lamb shoulder in a Kashmiri chilli and fennel gravy, finished with a spoon of ghee.',
    glutenFree: true,
    spicy: true,
    sizes: true,
    extras: [raita],
    featured: true,
    hue: 2,
  },
  {
    slug: 'smoky-aubergine-bharta',
    name: 'Smoky Aubergine Bharta',
    category: 'curries',
    price: 850,
    description:
      'Aubergine roasted over the coals until it collapses, then mashed with onion, tomato and green chilli.',
    diet: 'vegan',
    glutenFree: true,
    spicy: true,
    sizes: true,
    featured: true,
    hue: 280,
  },
  {
    slug: 'daal-makhani',
    name: 'Daal Makhani',
    category: 'curries',
    price: 895,
    description:
      'Black lentils simmered overnight with butter and cream. It is the dish our regulars order every single week.',
    diet: 'vegetarian',
    glutenFree: true,
    sizes: true,
    hue: 20,
  },
  {
    slug: 'butter-chicken',
    name: 'Butter Chicken',
    category: 'curries',
    price: 1225,
    description:
      'Tandoori chicken in a gentle tomato, butter and fenugreek sauce. A good first order if you are new to us.',
    glutenFree: true,
    spicy: true,
    sizes: true,
    extras: [raita],
    hue: 30,
  },
  {
    slug: 'chana-masala',
    name: 'Chana Masala',
    category: 'curries',
    price: 825,
    description:
      'Chickpeas in an onion and tomato masala, sharpened with dried mango powder and a little tamarind.',
    diet: 'vegan',
    glutenFree: true,
    spicy: true,
    sizes: true,
    hue: 38,
  },
  {
    slug: 'prawn-malabar-curry',
    name: 'Prawn Malabar Curry',
    category: 'curries',
    price: 1450,
    description:
      'King prawns in a coconut, curry leaf and kokum sauce, the way it is cooked along the Malabar coast.',
    glutenFree: true,
    spicy: true,
    sizes: true,
    hue: 22,
  },

  // Grill
  {
    slug: 'lamb-seekh-kebab',
    name: 'Lamb Seekh Kebab',
    category: 'grill',
    price: 1075,
    description:
      'Minced lamb with ginger, garlic and garam masala, pressed onto long skewers and cooked in the tandoor.',
    glutenFree: true,
    spicy: true,
    sizes: true,
    extras: [onions, mintDip],
    hue: 10,
  },
  {
    slug: 'tandoori-chicken',
    name: 'Tandoori Chicken (half)',
    category: 'grill',
    price: 1125,
    description:
      'Half a chicken marinated for a full day in yoghurt and Kashmiri chilli, then roasted in the clay oven.',
    glutenFree: true,
    spicy: true,
    extras: [onions, mintDip],
    hue: 4,
  },
  {
    slug: 'paneer-tikka',
    name: 'Paneer Tikka',
    category: 'grill',
    price: 975,
    description:
      'Thick slices of paneer, peppers and onion in a mustard oil and carom marinade, charred on the skewer.',
    diet: 'vegetarian',
    glutenFree: true,
    spicy: true,
    sizes: true,
    extras: [mintDip],
    hue: 36,
  },
  {
    slug: 'chicken-malai-tikka',
    name: 'Chicken Malai Tikka',
    category: 'grill',
    price: 1095,
    description:
      'Chicken thigh in a mild marinade of cream cheese, cardamom and white pepper, cooked until just charred.',
    glutenFree: true,
    sizes: true,
    extras: [mintDip],
    hue: 46,
  },
  {
    slug: 'amritsari-fish',
    name: 'Amritsari Fish',
    category: 'grill',
    price: 1250,
    description:
      'Fillets of hake in a light carom-seed batter, fried crisp and served with lemon and chaat masala.',
    extras: [mintDip],
    hue: 200,
  },

  // Rice and bread
  {
    slug: 'chicken-biryani',
    name: 'Chicken Biryani',
    category: 'rice-bread',
    price: 1295,
    description:
      'Layers of basmati, saffron and spiced chicken, sealed and cooked slowly in the pot, served with raita.',
    spicy: true,
    sizes: true,
    hue: 44,
  },
  {
    slug: 'vegetable-biryani',
    name: 'Vegetable Biryani',
    category: 'rice-bread',
    price: 1050,
    description:
      'Seasonal vegetables and basmati cooked with whole spices, fried onions and a little rose water.',
    diet: 'vegetarian',
    spicy: true,
    sizes: true,
    hue: 56,
  },
  {
    slug: 'jeera-rice',
    name: 'Jeera Rice',
    category: 'rice-bread',
    price: 375,
    description: 'Fluffy basmati rice tempered with cumin seeds and a bay leaf. It goes with everything.',
    diet: 'vegan',
    glutenFree: true,
    hue: 48,
  },
  {
    slug: 'garlic-naan',
    name: 'Garlic Naan',
    category: 'rice-bread',
    price: 325,
    description: 'Leavened bread slapped onto the wall of the tandoor and finished with garlic and coriander.',
    diet: 'vegetarian',
    extras: [butter],
    hue: 34,
  },
  {
    slug: 'peshwari-naan',
    name: 'Peshwari Naan',
    category: 'rice-bread',
    price: 375,
    description: 'A sweet naan stuffed with ground almonds, coconut and sultanas. Children love it.',
    diet: 'vegetarian',
    containsNuts: true,
    hue: 28,
  },
  {
    slug: 'tandoori-roti',
    name: 'Tandoori Roti',
    category: 'rice-bread',
    price: 225,
    description: 'A simple wholemeal flatbread baked in the clay oven, with no butter unless you ask.',
    diet: 'vegan',
    extras: [butter],
    hue: 24,
  },

  // Desserts and drinks
  {
    slug: 'mango-kulfi',
    name: 'Mango Kulfi',
    category: 'sweets',
    price: 450,
    description: 'Dense, slow-frozen milk ice cream with Alphonso mango, cut into slices to order.',
    diet: 'vegetarian',
    glutenFree: true,
    extras: [kulfi],
    featured: true,
    hue: 40,
  },
  {
    slug: 'gulab-jamun',
    name: 'Gulab Jamun',
    category: 'sweets',
    price: 425,
    description: 'Two warm milk dumplings soaked in a cardamom and rose syrup.',
    diet: 'vegetarian',
    featured: true,
    hue: 16,
  },
  {
    slug: 'gajar-halwa',
    name: 'Gajar Halwa',
    category: 'sweets',
    price: 475,
    description: 'Carrots grated and cooked down for hours with milk, ghee and cardamom, served warm.',
    diet: 'vegetarian',
    glutenFree: true,
    containsNuts: true,
    hue: 18,
  },
  {
    slug: 'mango-lassi',
    name: 'Mango Lassi',
    category: 'sweets',
    price: 395,
    description: 'A thick yoghurt drink blended with mango pulp and a pinch of cardamom.',
    diet: 'vegetarian',
    glutenFree: true,
    hue: 45,
  },
  {
    slug: 'masala-chai',
    name: 'Masala Chai',
    category: 'sweets',
    price: 275,
    description: 'Assam tea brewed with milk, ginger, cinnamon and black pepper. Sweetened unless you ask.',
    diet: 'vegetarian',
    glutenFree: true,
    hue: 26,
  },
]

export function dishBySlug(slug: string | undefined): Dish | undefined {
  return dishes.find((dish) => dish.slug === slug)
}

export function formatPrice(pence: number): string {
  return `£${(pence / 100).toFixed(2)}`
}
