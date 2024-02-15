#!/usr/bin/env python3
import base64
import hashlib
import hmac
import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

app = Flask(__name__)


def get_timestamp():
    return requests.get('https://yayawallet.com/api/en/time').json()['time']


def generate_signature(method, endpoint, body, timestamp):
    pre_hash_string = f"{timestamp}{method.upper()}{endpoint}{body}"
    hmac_digest = hmac.new(API_SECRET.encode(), pre_hash_string.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(hmac_digest).decode()
    return signature


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/en/transaction/find-by-user')
def find_by_user():
    timestamp = str(get_timestamp())
    endpoint = '/api/en/transaction/find-by-user'
    signature = generate_signature('GET', endpoint, '', timestamp)
    headers = {
        'YAYA-API-KEY': API_KEY,
        'YAYA-API-TIMESTAMP': timestamp,
        'YAYA-API-SIGN': signature,
    }
    response = requests.get(f'https://yayawallet.com{endpoint}', headers=headers)
    transactions = response.json()
    return transactions


if __name__ == '__main__':
    app.run(debug=True)
