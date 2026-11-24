from django.http import Http404
from django.shortcuts import render

from .data import BY_SLUG, CUISINES, DIETS, RECIPES, TIMES

MAX_SERVINGS = 12


def home(request):
    featured = [recipe for recipe in RECIPES if recipe.featured]
    quick = [recipe for recipe in RECIPES if recipe.minutes <= 25 and not recipe.featured][:4]
    return render(
        request,
        "recipes/home.html",
        {"featured": featured, "quick": quick, "cuisines": CUISINES, "total": len(RECIPES)},
    )


def _words(text: str) -> list[str]:
    return [word for word in text.lower().replace(",", " ").split() if word]


def matches(recipe, words: list[str]) -> bool:
    haystack = " ".join(
        [recipe.title, recipe.summary, recipe.cuisine, *(ing.name for ing in recipe.ingredients)]
    ).lower()
    return all(word in haystack for word in words)


def recipe_list(request):
    cuisine = request.GET.get("cuisine", "")
    diet = request.GET.get("diet", "")
    time = request.GET.get("time", "")
    query = request.GET.get("q", "").strip()
    found = list(RECIPES)
    if cuisine in CUISINES:
        found = [r for r in found if r.cuisine == cuisine]
    if diet in dict(DIETS):
        found = [r for r in found if diet in r.diets]
    if time.isdigit():
        found = [r for r in found if r.minutes <= int(time)]
    if query:
        found = [r for r in found if matches(r, _words(query))]
    filtered = bool(cuisine or diet or time or query)
    return render(
        request,
        "recipes/recipes.html",
        {
            "recipes": found,
            "cuisines": CUISINES,
            "diets": DIETS,
            "times": TIMES,
            "selected": {"cuisine": cuisine, "diet": diet, "time": time, "q": query},
            "filtered": filtered,
        },
    )


def recipe_detail(request, slug):
    recipe = BY_SLUG.get(slug)
    if recipe is None:
        raise Http404("No such recipe")
    try:
        servings = int(request.GET.get("servings", recipe.serves))
    except ValueError:
        servings = recipe.serves
    servings = max(1, min(MAX_SERVINGS, servings))
    factor = servings / recipe.serves
    more = [r for r in RECIPES if r.cuisine == recipe.cuisine and r.slug != recipe.slug][:3]
    return render(
        request,
        "recipes/recipe.html",
        {
            "recipe": recipe,
            "servings": servings,
            "fewer": servings - 1 if servings > 1 else None,
            "more_servings": servings + 1 if servings < MAX_SERVINGS else None,
            "ingredients": [ing.scaled(factor) for ing in recipe.ingredients],
            "more": more,
        },
    )
