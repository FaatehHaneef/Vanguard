"""Riverside Borough Council: public services website."""

import re
from itertools import count

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

# Postcode -> (area, collection day, next general waste date, next recycling date).
COLLECTIONS = {
    "RV1 1AA": ("Town Centre", "Monday", "Monday 23 November 2026", "Monday 30 November 2026"),
    "RV1 2BD": ("Town Centre", "Monday", "Monday 23 November 2026", "Monday 30 November 2026"),
    "RV1 3CF": ("Market Square", "Tuesday", "Tuesday 24 November 2026", "Tuesday 1 December 2026"),
    "RV1 4AB": ("Mill Lane and Weavers Row", "Thursday", "Thursday 26 November 2026", "Thursday 3 December 2026"),
    "RV1 4DE": ("Mill Lane and Weavers Row", "Thursday", "Thursday 26 November 2026", "Thursday 3 December 2026"),
    "RV1 5GH": ("Kingfisher Way", "Wednesday", "Wednesday 25 November 2026", "Wednesday 2 December 2026"),
    "RV1 6JK": ("Station Road", "Friday", "Friday 27 November 2026", "Friday 4 December 2026"),
    "RV2 1LM": ("Millford", "Monday", "Monday 23 November 2026", "Monday 30 November 2026"),
    "RV2 2NP": ("Millford", "Monday", "Monday 23 November 2026", "Monday 30 November 2026"),
    "RV2 3QR": ("Millford Green", "Tuesday", "Tuesday 24 November 2026", "Tuesday 1 December 2026"),
    "RV2 4ST": ("Ashby Close", "Wednesday", "Wednesday 25 November 2026", "Wednesday 2 December 2026"),
    "RV2 5UW": ("Northgate", "Thursday", "Thursday 26 November 2026", "Thursday 3 December 2026"),
    "RV2 6XY": ("Northgate", "Friday", "Friday 27 November 2026", "Friday 4 December 2026"),
    "RV3 1AB": ("Orchard Street", "Tuesday", "Tuesday 24 November 2026", "Tuesday 1 December 2026"),
    "RV3 2CD": ("Orchard Street", "Tuesday", "Tuesday 24 November 2026", "Tuesday 1 December 2026"),
    "RV3 3EF": ("Heron Meadows", "Wednesday", "Wednesday 25 November 2026", "Wednesday 2 December 2026"),
    "RV3 4GH": ("Heron Meadows", "Wednesday", "Wednesday 25 November 2026", "Wednesday 2 December 2026"),
    "RV3 5JL": ("Bridge End", "Friday", "Friday 27 November 2026", "Friday 4 December 2026"),
    "RV4 1MN": ("Eastbank", "Monday", "Monday 23 November 2026", "Monday 30 November 2026"),
    "RV4 2PQ": ("Eastbank", "Thursday", "Thursday 26 November 2026", "Thursday 3 December 2026"),
    "RV4 3RS": ("Eastbank Bridge", "Thursday", "Thursday 26 November 2026", "Thursday 3 December 2026"),
    "RV4 4TU": ("Wend Valley", "Friday", "Friday 27 November 2026", "Friday 4 December 2026"),
    "RV4 5WX": ("Wend Valley", "Tuesday", "Tuesday 24 November 2026", "Tuesday 1 December 2026"),
    "RV4 6YZ": ("Chapel Fields", "Wednesday", "Wednesday 25 November 2026", "Wednesday 2 December 2026"),
}

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Reports are kept in memory only, for as long as the server runs.
reports: dict[str, dict[str, str]] = {}
next_number = count(260411)


@app.get("/")
def home():
    return render_template("index.html")


def validate_report(form) -> tuple[dict[str, str], dict[str, str]]:
    values = {name: form.get(name, "").strip() for name in ("street", "description", "name", "email")}
    errors = {}
    if not values["street"]:
        errors["street"] = "Enter the street where the problem is"
    if len(values["description"]) < 10:
        errors["description"] = "Describe the problem in at least 10 characters"
    if not values["name"]:
        errors["name"] = "Enter your full name"
    if not EMAIL.match(values["email"]):
        errors["email"] = "Enter an email address in the correct format, like name@example.com"
    return values, errors


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html", values={}, errors={})
    values, errors = validate_report(request.form)
    if errors:
        return render_template("report.html", values=values, errors=errors), 400
    ref = f"R{next(next_number)}"
    reports[ref] = values
    return redirect(url_for("reported", ref=ref), code=303)


@app.get("/reported/<ref>")
def reported(ref: str):
    if ref not in reports:
        abort(404)
    return render_template("reported.html", ref=ref, report=reports[ref])


def normalise_postcode(text: str) -> str:
    compact = re.sub(r"\s+", "", text).upper()
    return f"{compact[:-3]} {compact[-3:]}" if len(compact) > 3 else compact


@app.get("/bins")
def bins():
    entered = request.args.get("postcode", "").strip()
    postcode = normalise_postcode(entered) if entered else ""
    error = ""
    collection = None
    if "postcode" in request.args:
        if not entered:
            error = "Enter a postcode"
        elif postcode not in COLLECTIONS:
            error = "We could not find that postcode. Check it is a Riverside postcode, like RV1 4AB"
        else:
            area, day, general, recycling = COLLECTIONS[postcode]
            collection = {"postcode": postcode, "area": area, "day": day,
                          "general": general, "recycling": recycling}
    areas = sorted({area for area, *_ in COLLECTIONS.values()})
    return render_template("bins.html", entered=entered, error=error,
                           collection=collection, areas=areas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3103)
