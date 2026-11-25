from django import forms

from .data import CUISINES


class SubmitRecipeForm(forms.Form):
    name = forms.CharField(max_length=80, error_messages={"required": "Enter your name."})
    email = forms.EmailField(
        error_messages={
            "required": "Enter your email address.",
            "invalid": "Enter an email address in the right format, like name@example.com.",
        }
    )
    title = forms.CharField(max_length=100, error_messages={"required": "Give your recipe a name."})
    cuisine = forms.ChoiceField(
        choices=[("", "Choose a cuisine")] + [(c, c) for c in CUISINES] + [("Other", "Other")],
        error_messages={"required": "Choose a cuisine, or Other."},
    )
    minutes = forms.IntegerField(
        min_value=1,
        max_value=600,
        error_messages={
            "required": "Enter how many minutes the recipe takes.",
            "invalid": "Enter the time as a whole number of minutes, like 35.",
            "min_value": "Enter a time of at least 1 minute.",
            "max_value": "Enter a time of 600 minutes or less.",
        },
    )
    serves = forms.IntegerField(
        min_value=1,
        max_value=12,
        error_messages={
            "required": "Enter how many people the recipe serves.",
            "invalid": "Enter the number of servings as a whole number, like 4.",
            "min_value": "A recipe must serve at least 1 person.",
            "max_value": "Enter 12 servings or fewer.",
        },
    )
    ingredients = forms.CharField(error_messages={"required": "List the ingredients, one on each line."})
    method = forms.CharField(error_messages={"required": "Describe how to make the recipe."})

    def clean_ingredients(self):
        lines = [line.strip() for line in self.cleaned_data["ingredients"].splitlines() if line.strip()]
        if len(lines) < 3:
            raise forms.ValidationError(
                "Put each ingredient on its own line, and list at least three. "
                "For example: chickpeas (new line) chopped tomatoes (new line) onion."
            )
        return lines

    def clean_method(self):
        method = self.cleaned_data["method"].strip()
        if len(method) < 20:
            raise forms.ValidationError("Describe the method in at least 20 characters.")
        return method
