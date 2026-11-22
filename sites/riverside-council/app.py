"""Riverside Borough Council: public services website."""

import re
from itertools import count

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3103)
