#!/usr/bin/env python3
import base64
import hashlib
import hmac
import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

app = Flask(__name__)


def get_timestamp():
    return requests.get("https://yayawallet.com/api/en/time").json()["time"]


def generate_signature(method, endpoint, body, timestamp):
    pre_hash_string = f"{timestamp}{method.upper()}{endpoint}{body}"
    hmac_digest = hmac.new(
        API_SECRET.encode(),
        pre_hash_string.encode(),
        hashlib.sha256,
    ).digest()
    signature = base64.b64encode(hmac_digest).decode()
    return signature


def make_request(method, endpoint, body=None):
    timestamp = str(get_timestamp())
    if body is None:
        body = ""
    signature = generate_signature(method, endpoint, body, timestamp)
    headers = {
        "YAYA-API-KEY": API_KEY,
        "YAYA-API-TIMESTAMP": timestamp,
        "YAYA-API-SIGN": signature,
    }
    if method == "GET":
        response = requests.get(
            f"https://yayawallet.com{endpoint}",
            headers=headers,
        )
    elif method == "POST":
        headers["Content-type"] = "application/json"
        response = requests.post(
            f"https://yayawallet.com{endpoint}",
            headers=headers,
            data=body,
        )
    else:
        raise ValueError("Unsupported HTTP method")
    return response.json()


def get_find_by_user():
    endpoint = "/api/en/transaction/find-by-user"
    return make_request(
        "GET",
        endpoint,
    )


def get_search(query):
    body = f'{{"query": "{query}"}}'
    endpoint = "/api/en/transaction/search"
    return make_request(
        "POST",
        endpoint,
        body,
    )


def get_user_profile(account_name: str):
    body = f'{{"account_name": "{account_name}"}}'
    endpoint = "/api/en/user/profile"
    return make_request(
        "POST",
        endpoint,
        body,
    )


@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    transactions = get_find_by_user()["data"]
    return render_template(
        "index.html",
        transactions=transactions,
    )


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile_page():
    profile = get_user_profile("antenehgebey")
    return render_template(
        "profile.html",
        profile=profile,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
