import requests
import os

from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from dotenv import load_dotenv


# Load key-value pairs from .env into memory
load_dotenv()

# Retrieve the key securely
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def get_hobby_image_url(hobby_name):
    """Fetch a high-quality thumbnail image URL for a given hobby name using unsplash API."""
    if not UNSPLASH_ACCESS_KEY:
        return "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=600&q=80"
    
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": hobby_name,
            "per_page": 1,
            "orientation": "landscape",
            "client_id": UNSPLASH_ACCESS_KEY
        }
        
        response = requests.get(url, params=params, timeout=3)
        data = response.json()
        
        if data.get("results"):
            return data["results"][0]["urls"]["small"]
    except Exception:
        pass
    
    return "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=600&q=80"

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

def render_with_flash(message: str, category: str, page: str, **kwargs):
    flash(message, category)
    return render_template(page, **kwargs)