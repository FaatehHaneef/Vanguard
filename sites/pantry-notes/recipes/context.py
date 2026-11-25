"""Template context shared by every page."""


def shopping_list(request):
    saved = request.session.get("list", {})
    return {"list_count": len(saved)}
