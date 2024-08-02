import csv
import datetime
import pytz
import requests
import urllib
import uuid
import pint


from flask import redirect, render_template, request, session
from functools import wraps

ureg = pint.UnitRegistry()

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def convert_to_standard_unit(quantity, unit):
    try:
        measurement = quantity * ureg(unit)
        standard_measurement = measurement.to_base_units()
        return standard_measurement.magnitude, str(standard_measurement.units)
    except ValueError:
        return None

def format_quantity(quantity, unit):
    measurement = quantity * ureg(unit)
    return measurement.magnitude, str(measurement.units)
