from itertools import count

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .data import BY_SLUG, CUISINES, DIETS, RECIPES, TIMES
from .forms import SubmitRecipeForm

MAX_SERVINGS = 12
SORTS = {
    "recommended": ("Recommended", None),
    "quickest": ("Quickest first", lambda r: (r.minutes, r.title)),
    "fewest": ("Fewest ingredients", lambda r: (len(r.ingredients), r.title)),
    "name": ("Name, A to Z", lambda r: r.title),
}

# Submitted recipes are kept in memory only, for as long as the server runs.
submissions: dict[int, dict] = {}
next_submission = count(1042)


def home(request):
    featured = [recipe for recipe in RECIPES if recipe.featured]
    quick = [recipe for recipe in RECIPES if recipe.minutes <= 25 and not recipe.featured][:4]
    return render(
        request,
        "recipes/home.html",
        {"featured": featured, "quick": quick, "cuisines": CUISINES, "total": len(RECIPES)},
    )


def about(request):
    return render(request, "recipes/about.html")


def club(request):
    return render(request, "recipes/club.html")


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
    sort = request.GET.get("sort", "recommended")
    if sort not in SORTS:
        sort = "recommended"
    key = SORTS[sort][1]
    if key is not None:
        found.sort(key=key)
    filtered = bool(cuisine or diet or time or query)
    params = request.GET.copy()
    params.pop("sort", None)
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
            "sorts": [(value, label) for value, (label, _) in SORTS.items()],
            "sort": sort,
            "sort_label": SORTS[sort][0],
            "base_query": params.urlencode(),
        },
    )


def _recipe(slug):
    recipe = BY_SLUG.get(slug)
    if recipe is None:
        raise Http404("No such recipe")
    return recipe


def _servings(value, default: int) -> int:
    try:
        servings = int(value)
    except (TypeError, ValueError):
        servings = default
    return max(1, min(MAX_SERVINGS, servings))


def recipe_detail(request, slug):
    recipe = _recipe(slug)
    servings = _servings(request.GET.get("servings"), recipe.serves)
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
            "on_list": request.session.get("list", {}).get(recipe.slug),
        },
    )


@require_POST
def list_add(request, slug):
    recipe = _recipe(slug)
    servings = _servings(request.POST.get("servings"), recipe.serves)
    saved = dict(request.session.get("list", {}))
    saved[recipe.slug] = servings
    request.session["list"] = saved
    messages.success(
        request, f"Added the ingredients for {recipe.title} ({servings} servings) to your shopping list."
    )
    back = request.POST.get("next", "")
    if not back.startswith("/") or back[1:2] in ("/", "\\"):
        back = reverse("recipe", args=[recipe.slug])
    return redirect(back)


@require_POST
def list_remove(request, slug):
    saved = dict(request.session.get("list", {}))
    if saved.pop(slug, None) is not None and slug in BY_SLUG:
        messages.success(request, f"Removed {BY_SLUG[slug].title} from your shopping list.")
    request.session["list"] = saved
    return redirect("shopping_list")


@require_POST
def list_clear(request):
    request.session["list"] = {}
    messages.success(request, "Your shopping list is empty.")
    return redirect("shopping_list")


def shopping_list(request):
    saved = request.session.get("list", {})
    entries = []
    for slug, servings in saved.items():
        recipe = BY_SLUG.get(slug)
        if recipe is None:
            continue
        factor = servings / recipe.serves
        entries.append(
            {
                "recipe": recipe,
                "servings": servings,
                "lines": [ing.scaled(factor) for ing in recipe.ingredients],
            }
        )
    return render(request, "recipes/list.html", {"entries": entries})


def submit(request):
    form = SubmitRecipeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        number = next(next_submission)
        submissions[number] = form.cleaned_data
        return redirect("submitted", number=number)
    return render(request, "recipes/submit.html", {"form": form}, status=400 if form.errors else 200)


def submitted(request, number):
    submission = submissions.get(number)
    if submission is None:
        raise Http404("No such submission")
    return render(request, "recipes/submitted.html", {"number": number, "submission": submission})
