"""Every recipe on the site, with fixed content.

Quantities are for the recipe's own number of servings and are scaled on the recipe
page. A quantity of None means "to taste" or "a handful": it is never scaled.
"""

from dataclasses import dataclass
from fractions import Fraction

from django.utils.safestring import mark_safe

from .art import ART


@dataclass(frozen=True)
class Ingredient:
    quantity: float | None
    unit: str
    name: str

    def scaled(self, factor: float) -> str:
        if self.quantity is None:
            return self.name
        amount = self.quantity * factor
        unit = f" {self.unit}" if self.unit else ""
        return f"{format_amount(amount)}{unit} {self.name}"


def format_amount(amount: float) -> str:
    """1.5 -> '1½', 0.25 -> '¼', 2.0 -> '2', 333.3 -> '330' (kitchen-friendly)."""
    if amount >= 20:
        return str(int(round(amount / 5) * 5))
    whole = int(amount)
    rest = Fraction(amount - whole).limit_denominator(4)
    fractions = {Fraction(1, 4): "¼", Fraction(1, 2): "½", Fraction(3, 4): "¾"}
    if rest == 0:
        return str(whole)
    if rest == 1:
        return str(whole + 1)
    if rest in fractions:
        return f"{whole or ''}{fractions[rest]}"
    return f"{amount:.1f}".rstrip("0").rstrip(".")


@dataclass(frozen=True)
class Recipe:
    slug: str
    title: str
    cuisine: str
    minutes: int
    serves: int
    diets: tuple[str, ...]
    summary: str
    art: str
    ingredients: tuple[Ingredient, ...]
    steps: tuple[str, ...]
    featured: bool = False
    tip: str = ""

    @property
    def art_svg(self):
        return mark_safe(ART.get(self.art, ART["bowl"]))


def i(quantity, unit, name):
    return Ingredient(quantity, unit, name)


RECIPES = [
    Recipe(
        "red-lentil-dal", "Red lentil dal with crispy onions", "Indian", 35, 4, ("vegan", "gluten-free"),
        "A thick, gently spiced dal finished with a sizzle of cumin seeds and onions fried until golden.",
        "curry",
        (i(250, "g", "red lentils, rinsed"), i(1, "litre", "water"), i(1, "tsp", "ground turmeric"),
         i(2, "", "onions, thinly sliced"), i(3, "tbsp", "sunflower oil"), i(2, "tsp", "cumin seeds"),
         i(3, "", "garlic cloves, sliced"), i(1, "", "green chilli, split"), i(None, "", "salt and lemon juice to taste")),
        ("Simmer the lentils in the water with the turmeric for 25 minutes, stirring now and then, until soft and thick.",
         "Meanwhile fry the onions in the oil over a medium heat for 15 minutes until deep golden. Lift half out to drain.",
         "Add the cumin seeds, garlic and chilli to the pan and fry for a minute, then tip everything into the dal.",
         "Season with salt and lemon juice and serve topped with the crispy onions."),
        featured=True, tip="The dal thickens as it stands. Loosen it with a splash of hot water before serving.",
    ),
    Recipe(
        "chicken-tikka-traybake", "Chicken tikka traybake", "Indian", 50, 4, ("gluten-free",),
        "Yoghurt-marinated chicken thighs roasted on one tray with peppers, red onion and potatoes.",
        "tray",
        (i(8, "", "boneless chicken thighs"), i(150, "g", "natural yoghurt"), i(2, "tbsp", "tikka paste"),
         i(500, "g", "new potatoes, halved"), i(2, "", "red peppers, in chunks"), i(1, "", "red onion, in wedges"),
         i(2, "tbsp", "oil"), i(None, "", "coriander leaves to serve")),
        ("Heat the oven to 220°C (200°C fan). Mix the yoghurt and tikka paste and coat the chicken in it.",
         "Toss the potatoes in the oil on a large tray and roast for 15 minutes.",
         "Add the peppers, onion and chicken, and roast for 30 minutes more, until the chicken is charred at the edges.",
         "Scatter with coriander and serve with the juices from the tray."),
    ),
    Recipe(
        "saag-paneer", "Saag paneer", "Indian", 30, 4, ("vegetarian", "gluten-free"),
        "Golden cubes of paneer in a silky spinach sauce, ready in half an hour.",
        "greens",
        (i(225, "g", "paneer, in cubes"), i(500, "g", "spinach"), i(1, "", "onion, finely chopped"),
         i(2, "", "garlic cloves, grated"), i(1, "tbsp", "ginger, grated"), i(1, "tsp", "garam masala"),
         i(3, "tbsp", "double cream"), i(2, "tbsp", "ghee or oil")),
        ("Fry the paneer in half the ghee until golden on every side, then set aside.",
         "Wilt the spinach in a large pan, squeeze out the water and chop it finely.",
         "Fry the onion in the rest of the ghee for 8 minutes, add the garlic, ginger and garam masala, then the spinach and cream.",
         "Stir the paneer back in and warm through for 3 minutes."),
    ),
    Recipe(
        "chana-masala", "Chana masala", "Indian", 40, 4, ("vegan", "gluten-free"),
        "Chickpeas in a tangy tomato and onion gravy, even better the next day.",
        "curry",
        (i(2, "tins", "chickpeas (400 g each), drained"), i(1, "tin", "chopped tomatoes (400 g)"), i(2, "", "onions, chopped"),
         i(3, "", "garlic cloves"), i(1, "tbsp", "ginger, grated"), i(2, "tsp", "chana masala spice"),
         i(1, "tsp", "amchur (dried mango powder)"), i(3, "tbsp", "oil")),
        ("Fry the onions in the oil for 12 minutes, until well browned.",
         "Add the garlic, ginger and spices and cook for 2 minutes.",
         "Add the tomatoes and cook down for 10 minutes, then the chickpeas and 200 ml water.",
         "Simmer for 15 minutes, crushing a few chickpeas to thicken the sauce."),
    ),
    Recipe(
        "lemon-herb-risotto", "Lemon and herb risotto", "Italian", 40, 4, ("vegetarian", "gluten-free"),
        "A bright, creamy risotto with lemon zest, parsley, mint and plenty of parmesan.",
        "risotto",
        (i(300, "g", "risotto rice"), i(1.2, "litres", "hot vegetable stock"), i(1, "", "onion, finely chopped"),
         i(50, "g", "butter"), i(125, "ml", "dry white wine"), i(1, "", "lemon, zest and juice"),
         i(60, "g", "parmesan, grated"), i(None, "", "a handful of parsley and mint")),
        ("Soften the onion in half the butter for 8 minutes.",
         "Stir in the rice for a minute, then add the wine and let it bubble away.",
         "Add the stock a ladle at a time, stirring, for about 20 minutes until the rice is just tender.",
         "Beat in the rest of the butter, the parmesan, lemon and herbs, then rest for 2 minutes."),
        featured=True,
    ),
    Recipe(
        "spaghetti-puttanesca", "Spaghetti puttanesca", "Italian", 20, 4, (),
        "The store-cupboard classic: tomatoes, olives, capers and anchovies in the time the pasta takes to cook.",
        "pasta",
        (i(400, "g", "spaghetti"), i(1, "tin", "chopped tomatoes (400 g)"), i(6, "", "anchovy fillets"),
         i(2, "tbsp", "capers"), i(100, "g", "black olives, halved"), i(3, "", "garlic cloves, sliced"),
         i(1, "pinch", "chilli flakes"), i(3, "tbsp", "olive oil")),
        ("Cook the spaghetti in well-salted boiling water.",
         "Meanwhile warm the oil with the garlic, chilli and anchovies until the anchovies melt.",
         "Add the tomatoes, capers and olives and simmer for 8 minutes.",
         "Toss with the drained pasta and a splash of the cooking water."),
    ),
    Recipe(
        "mushroom-lasagne", "Mushroom and spinach lasagne", "Italian", 90, 6, ("vegetarian",),
        "Layers of garlicky mushrooms, spinach and a light béchamel, baked until bubbling.",
        "lasagne",
        (i(12, "", "lasagne sheets"), i(750, "g", "mushrooms, sliced"), i(300, "g", "spinach"),
         i(3, "", "garlic cloves"), i(60, "g", "butter"), i(60, "g", "plain flour"), i(800, "ml", "milk"),
         i(100, "g", "mozzarella"), i(50, "g", "parmesan")),
        ("Fry the mushrooms in batches until browned, add the garlic, then wilt in the spinach.",
         "Melt the butter, stir in the flour, then whisk in the milk and simmer until thick.",
         "Layer sheets, mushrooms and sauce three times, ending with sauce, mozzarella and parmesan.",
         "Bake at 190°C (170°C fan) for 45 minutes and rest for 10 minutes before cutting."),
    ),
    Recipe(
        "minestrone", "Winter minestrone", "Italian", 45, 6, ("vegan",),
        "A big pot of vegetable and bean soup with small pasta, finished with olive oil.",
        "soup",
        (i(2, "", "carrots, diced"), i(2, "", "celery sticks, diced"), i(1, "", "onion, diced"),
         i(1, "tin", "cannellini beans (400 g)"), i(1, "tin", "chopped tomatoes (400 g)"), i(1.5, "litres", "vegetable stock"),
         i(100, "g", "small pasta"), i(150, "g", "cavolo nero, shredded"), i(3, "tbsp", "olive oil")),
        ("Soften the onion, carrot and celery in the oil for 10 minutes.",
         "Add the tomatoes and stock and simmer for 15 minutes.",
         "Add the pasta and beans and cook for 10 minutes, adding the cavolo nero for the last 3.",
         "Serve with more olive oil poured over."),
    ),
    Recipe(
        "black-bean-tacos", "Smoky black bean tacos", "Mexican", 25, 4, ("vegan",),
        "Chipotle black beans, quick-pickled onions and a crunchy slaw in warm corn tortillas.",
        "taco",
        (i(2, "tins", "black beans (400 g each), drained"), i(1, "tbsp", "chipotle paste"), i(1, "tsp", "ground cumin"),
         i(12, "", "small corn tortillas"), i(1, "", "red onion, thinly sliced"), i(2, "", "limes"),
         i(200, "g", "red cabbage, shredded"), i(1, "", "avocado"), i(None, "", "coriander to serve")),
        ("Toss the onion with the juice of one lime and a pinch of salt and leave to pickle.",
         "Warm the beans with the chipotle paste, cumin and a splash of water, crushing a few.",
         "Dress the cabbage with the remaining lime.",
         "Warm the tortillas and fill with beans, slaw, avocado, pickled onions and coriander."),
        featured=True,
    ),
    Recipe(
        "chicken-enchiladas", "Green chicken enchiladas", "Mexican", 55, 4, (),
        "Tortillas rolled around shredded chicken, baked in a tangy tomatillo salsa with cheese.",
        "tray",
        (i(500, "g", "cooked chicken, shredded"), i(8, "", "flour tortillas"), i(500, "ml", "salsa verde"),
         i(150, "g", "cheddar, grated"), i(150, "g", "soured cream"), i(1, "", "onion, chopped"),
         i(None, "", "jalapeños and coriander to serve")),
        ("Heat the oven to 200°C (180°C fan).", "Mix the chicken with the onion and half the salsa.",
         "Roll the filling in the tortillas and lay them in a dish.",
         "Pour over the rest of the salsa, cover with cheese and bake for 25 minutes. Serve with soured cream."),
    ),
    Recipe(
        "pozole-verde", "Pozole verde with beans", "Mexican", 60, 6, ("vegan", "gluten-free"),
        "A hearty green hominy and bean stew with pumpkin seeds, served with radishes and lime.",
        "soup",
        (i(2, "tins", "hominy (400 g each)"), i(1, "tin", "pinto beans (400 g)"), i(500, "g", "tomatillos"),
         i(2, "", "green chillies"), i(50, "g", "pumpkin seeds"), i(1, "", "onion"), i(1.5, "litres", "vegetable stock"),
         i(None, "", "radishes, lime and oregano to serve")),
        ("Blend the tomatillos, chillies, pumpkin seeds and half the onion until smooth.",
         "Fry the sauce in a large pan for 10 minutes until it darkens.",
         "Add the stock, hominy and beans and simmer for 30 minutes.",
         "Serve with sliced radishes, lime and a pinch of oregano."),
    ),
    Recipe(
        "miso-aubergine", "Miso-glazed aubergine", "Japanese", 35, 2, ("vegan",),
        "Aubergine halves roasted until silky, then grilled under a sweet, salty miso glaze.",
        "aubergine",
        (i(2, "", "aubergines, halved lengthways"), i(3, "tbsp", "white miso"), i(1, "tbsp", "mirin"),
         i(1, "tbsp", "maple syrup"), i(1, "tsp", "rice vinegar"), i(1, "tbsp", "sesame oil"),
         i(None, "", "sesame seeds and spring onion to serve")),
        ("Heat the oven to 200°C (180°C fan). Score the aubergine flesh, brush with the sesame oil and roast cut side up for 25 minutes.",
         "Mix the miso, mirin, maple syrup and vinegar.",
         "Spread the glaze over the aubergines and grill for 3 to 4 minutes until bubbling.",
         "Scatter with sesame seeds and spring onion."),
    ),
    Recipe(
        "katsu-curry", "Chicken katsu curry", "Japanese", 50, 4, (),
        "Panko-crumbed chicken with a mild, fruity curry sauce and sticky rice.",
        "katsu",
        (i(4, "", "chicken breasts, flattened"), i(100, "g", "panko breadcrumbs"), i(2, "", "eggs, beaten"),
         i(50, "g", "plain flour"), i(1, "", "onion"), i(2, "", "carrots"), i(2, "tbsp", "curry powder"),
         i(500, "ml", "chicken stock"), i(300, "g", "sushi rice")),
        ("Soften the onion and carrots, stir in the curry powder and a tablespoon of flour, then add the stock and simmer for 20 minutes. Blend smooth.",
         "Cook the rice.", "Coat the chicken in flour, egg and panko, then shallow-fry for 4 minutes a side.",
         "Slice the chicken and serve over rice with the sauce."),
    ),
    Recipe(
        "salmon-teriyaki-bowl", "Salmon teriyaki rice bowl", "Japanese", 25, 2, ("gluten-free",),
        "Glossy teriyaki salmon over rice with quick cucumber pickles and edamame.",
        "bowl",
        (i(2, "", "salmon fillets"), i(3, "tbsp", "tamari"), i(2, "tbsp", "mirin"), i(1, "tbsp", "honey"),
         i(150, "g", "sushi rice"), i(100, "g", "edamame"), i(0.5, "", "cucumber"), i(1, "tbsp", "rice vinegar")),
        ("Cook the rice. Slice the cucumber thinly and toss with the vinegar and a pinch of salt.",
         "Mix the tamari, mirin and honey.", "Fry the salmon skin side down for 5 minutes, turn, add the sauce and bubble until sticky.",
         "Serve on the rice with the cucumber and edamame."),
    ),
    Recipe(
        "shakshuka", "Shakshuka", "Middle Eastern", 30, 2, ("vegetarian", "gluten-free"),
        "Eggs baked in a spiced pepper and tomato sauce, served straight from the pan.",
        "pan",
        (i(4, "", "eggs"), i(1, "tin", "chopped tomatoes (400 g)"), i(2, "", "red peppers, sliced"),
         i(1, "", "onion, sliced"), i(2, "", "garlic cloves"), i(1, "tsp", "cumin"), i(1, "tsp", "smoked paprika"),
         i(50, "g", "feta"), i(2, "tbsp", "olive oil")),
        ("Cook the onion and peppers in the oil for 10 minutes until soft.",
         "Add the garlic and spices for a minute, then the tomatoes, and simmer for 10 minutes.",
         "Make four hollows, crack in the eggs, cover and cook for 6 to 8 minutes.",
         "Crumble over the feta and serve with bread."),
    ),
    Recipe(
        "falafel-wraps", "Baked falafel wraps", "Middle Eastern", 45, 4, ("vegan",),
        "Herby baked falafel in flatbreads with tahini sauce, pickles and salad.",
        "wrap",
        (i(2, "tins", "chickpeas (400 g each), drained"), i(1, "", "onion"), i(30, "g", "parsley"),
         i(2, "tsp", "ground cumin"), i(3, "tbsp", "plain flour"), i(4, "", "flatbreads"), i(3, "tbsp", "tahini"),
         i(1, "", "lemon"), i(None, "", "pickles, tomato and lettuce")),
        ("Heat the oven to 200°C (180°C fan). Blitz the chickpeas, onion, parsley, cumin and flour to a rough paste.",
         "Shape into 16 balls, flatten slightly and bake on an oiled tray for 25 minutes, turning once.",
         "Whisk the tahini with the lemon juice and enough water to make a pouring sauce.",
         "Fill the flatbreads with falafel, salad, pickles and sauce."),
    ),
    Recipe(
        "lamb-kofta", "Lamb kofta with herby yoghurt", "Middle Eastern", 30, 4, ("gluten-free",),
        "Spiced lamb skewers grilled until charred, with a cool yoghurt and mint dip.",
        "skewer",
        (i(500, "g", "minced lamb"), i(1, "", "onion, grated"), i(2, "tsp", "ground cumin"), i(1, "tsp", "ground coriander"),
         i(200, "g", "Greek yoghurt"), i(None, "", "a handful of mint"), i(1, "", "lemon")),
        ("Mix the lamb, onion and spices and shape around eight skewers.",
         "Grill or griddle for 10 to 12 minutes, turning until charred.",
         "Stir the chopped mint and lemon juice into the yoghurt.", "Serve the kofta with the yoghurt and salad."),
    ),
    Recipe(
        "fish-pie", "Smoked haddock fish pie", "British", 75, 6, (),
        "Smoked haddock, salmon and prawns in a creamy sauce under a cheesy mash lid.",
        "pie",
        (i(1, "kg", "floury potatoes"), i(400, "g", "smoked haddock"), i(300, "g", "salmon"), i(150, "g", "prawns"),
         i(600, "ml", "milk"), i(50, "g", "butter"), i(50, "g", "plain flour"), i(80, "g", "cheddar"),
         i(None, "", "a handful of parsley")),
        ("Boil and mash the potatoes with a knob of butter.",
         "Poach the haddock and salmon in the milk for 5 minutes, then flake the fish and keep the milk.",
         "Make a sauce with the butter, flour and poaching milk, then stir in the fish, prawns and parsley.",
         "Top with the mash and cheese and bake at 200°C (180°C fan) for 30 minutes."),
    ),
    Recipe(
        "leek-potato-soup", "Leek and potato soup", "British", 40, 4, ("vegetarian", "gluten-free"),
        "A smooth, comforting soup that needs only a handful of ingredients.",
        "soup",
        (i(3, "", "leeks, sliced"), i(500, "g", "potatoes, diced"), i(1, "", "onion"), i(40, "g", "butter"),
         i(1, "litre", "vegetable stock"), i(100, "ml", "double cream"), i(None, "", "chives to serve")),
        ("Melt the butter and soften the leeks and onion for 10 minutes without browning.",
         "Add the potatoes and stock and simmer for 20 minutes.", "Blend until smooth and stir in the cream.",
         "Season and serve with chopped chives."),
    ),
    Recipe(
        "apple-crumble", "Apple and blackberry crumble", "British", 55, 6, ("vegetarian",),
        "Tart apples and blackberries under a buttery oat crumble.",
        "crumble",
        (i(800, "g", "Bramley apples"), i(200, "g", "blackberries"), i(50, "g", "caster sugar"),
         i(150, "g", "plain flour"), i(100, "g", "cold butter"), i(75, "g", "demerara sugar"), i(50, "g", "rolled oats")),
        ("Heat the oven to 190°C (170°C fan). Peel and chop the apples and mix with the blackberries and caster sugar in a dish.",
         "Rub the butter into the flour, then stir in the demerara sugar and oats.",
         "Scatter the crumble over the fruit.", "Bake for 35 to 40 minutes until golden and bubbling."),
    ),
    Recipe(
        "thai-green-curry", "Thai green vegetable curry", "Thai", 30, 4, ("vegan", "gluten-free"),
        "Coconut, green curry paste, crunchy vegetables and Thai basil, ready in half an hour.",
        "curry",
        (i(3, "tbsp", "green curry paste (vegan)"), i(1, "tin", "coconut milk (400 ml)"), i(200, "g", "green beans"),
         i(1, "", "courgette"), i(200, "g", "baby corn"), i(200, "g", "firm tofu"), i(1, "tbsp", "soy sauce"),
         i(None, "", "Thai basil and lime to serve")),
        ("Fry the curry paste in a splash of the coconut milk for 2 minutes.",
         "Add the rest of the coconut milk and 150 ml water and bring to a simmer.",
         "Add the vegetables and tofu and cook for 6 minutes until just tender.",
         "Season with soy sauce and serve with basil and lime."),
    ),
    Recipe(
        "pad-thai", "Prawn pad thai", "Thai", 25, 2, (),
        "Rice noodles stir-fried with prawns, egg, tamarind and peanuts.",
        "noodles",
        (i(150, "g", "flat rice noodles"), i(200, "g", "raw prawns"), i(2, "", "eggs"), i(2, "tbsp", "tamarind paste"),
         i(2, "tbsp", "fish sauce"), i(1, "tbsp", "brown sugar"), i(100, "g", "beansprouts"), i(40, "g", "roasted peanuts")),
        ("Soak the noodles in hot water for 10 minutes and drain.",
         "Stir-fry the prawns for 2 minutes, push aside and scramble in the eggs.",
         "Add the noodles, tamarind, fish sauce and sugar and toss for 2 minutes.",
         "Stir in the beansprouts and serve with chopped peanuts and lime."),
    ),
    Recipe(
        "greek-salad", "Greek salad with crispy chickpeas", "Greek", 20, 2, ("vegetarian", "gluten-free"),
        "The classic salad with oregano-roasted chickpeas for crunch.",
        "salad",
        (i(1, "tin", "chickpeas (400 g)"), i(4, "", "ripe tomatoes"), i(1, "", "cucumber"), i(0.5, "", "red onion"),
         i(100, "g", "feta"), i(60, "g", "Kalamata olives"), i(1, "tsp", "dried oregano"), i(3, "tbsp", "olive oil")),
        ("Roast the drained chickpeas with a spoon of the oil and the oregano at 220°C (200°C fan) for 15 minutes.",
         "Chop the tomatoes, cucumber and onion into chunks.",
         "Toss with the olives and the rest of the oil.", "Top with the feta and the warm chickpeas."),
    ),
    Recipe(
        "spanakopita", "Spanakopita", "Greek", 70, 6, ("vegetarian",),
        "A crisp filo pie filled with spinach, feta, dill and spring onions.",
        "pie",
        (i(270, "g", "filo pastry"), i(500, "g", "spinach"), i(200, "g", "feta"), i(2, "", "eggs"),
         i(6, "", "spring onions"), i(None, "", "a bunch of dill"), i(80, "g", "butter, melted")),
        ("Wilt and squeeze the spinach, then mix with the feta, eggs, spring onions and dill.",
         "Brush half the filo sheets with butter and layer them in a tin.",
         "Spread over the filling and top with the rest of the buttered filo.",
         "Score the top and bake at 190°C (170°C fan) for 40 minutes."),
    ),
]

BY_SLUG = {recipe.slug: recipe for recipe in RECIPES}
CUISINES = sorted({recipe.cuisine for recipe in RECIPES})
DIETS = [("vegan", "Vegan"), ("vegetarian", "Vegetarian"), ("gluten-free", "Gluten-free")]
TIMES = [(20, "20 minutes or less"), (30, "30 minutes or less"), (45, "45 minutes or less"), (60, "1 hour or less")]
