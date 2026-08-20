"""
포트폴리오 실시간 시세 앱
Render / Railway / Fly.io 배포용
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import urllib.request
import json
import time
import traceback
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# __file__ 기준으로 경로 고정 (gunicorn에서도 안전)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

app = Flask(__name__)
CORS(app)

_cache = {}
_CACHE_TTL = 60


def fetch_yahoo_price(ticker: str) -> dict:
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return {"ticker": ticker, "price": None, "error": "empty ticker"}

    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _CACHE_TTL:
        return _cache[ticker]["data"]

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        result = data.get("chart", {}).get("result")
        if not result:
            out = {"ticker": ticker, "price": None, "error": "no data"}
        else:
            meta = result[0].get("meta", {})
            price = meta.get("regularMarketPrice") or meta.get("previousClose")
            out = {
                "ticker": ticker,
                "price": price,
                "currency": meta.get("currency", "USD"),
                "name": meta.get("shortName") or meta.get("symbol", ticker),
                "error": None,
            }
        _cache[ticker] = {"ts": now, "data": out}
        return out
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e)}


@app.route("/")
def index():
    try:
        if not os.path.exists(TEMPLATE_PATH):
            # 디버그 정보 반환
            files = []
            try:
                files = os.listdir(BASE_DIR)
            except Exception:
                pass
            return Response(
                f"<h1>Template not found</h1>"
                f"<p>Looking for: {TEMPLATE_PATH}</p>"
                f"<p>BASE_DIR: {BASE_DIR}</p>"
                f"<p>Files in BASE_DIR: {files}</p>",
                status=500,
                mimetype="text/html",
            )
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        return Response(html, mimetype="text/html")
    except Exception:
        return Response(
            f"<h1>Error loading page</h1><pre>{traceback.format_exc()}</pre>",
            status=500,
            mimetype="text/html",
        )


@app.route("/api/quotes")
def api_quotes():
    try:
        symbols_param = request.args.get("symbols", "")
        symbols = [s.strip().upper() for s in symbols_param.split(",") if s.strip()]

        if not symbols:
            return jsonify({"error": "symbols parameter required"}), 400
        if len(symbols) > 30:
            return jsonify({"error": "too many symbols (max 30)"}), 400

        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(fetch_yahoo_price, s): s for s in symbols}
            for fut in as_completed(futures):
                data = fut.result()
                results[data["ticker"]] = data

        return jsonify({
            "quotes": results,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        })
    except Exception:
        return jsonify({
            "error": "server error",
            "trace": traceback.format_exc(),
        }), 500


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "template_exists": os.path.exists(TEMPLATE_PATH),
        "base_dir": BASE_DIR,
    })


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "error": str(e),
        "trace": traceback.format_exc(),
    }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
