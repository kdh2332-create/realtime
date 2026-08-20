"""
포트폴리오 실시간 시세 앱
- Yahoo Finance 시세를 서버에서 가져와 CORS 문제 없이 제공
- Render / Railway / Fly.io 등에 배포 가능
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import urllib.request
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

# 간단한 메모리 캐시 (60초)
_cache = {}
_CACHE_TTL = 60


def fetch_yahoo_price(ticker: str) -> dict:
    """Yahoo Finance chart API에서 현재가 조회"""
    ticker = ticker.strip().upper()
    if not ticker:
        return {"ticker": ticker, "price": None, "error": "empty ticker"}

    # 캐시 확인
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _CACHE_TTL:
        return _cache[ticker]["data"]

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
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
    return render_template("index.html")


@app.route("/api/quotes")
def api_quotes():
    """
    GET /api/quotes?symbols=QLD,SPYM,TQQQ
    여러 티커의 현재가를 한 번에 반환
    """
    symbols_param = request.args.get("symbols", "")
    symbols = [s.strip().upper() for s in symbols_param.split(",") if s.strip()]

    if not symbols:
        return jsonify({"error": "symbols parameter required"}), 400

    if len(symbols) > 30:
        return jsonify({"error": "too many symbols (max 30)"}), 400

    results = {}
    # 병렬 요청 (최대 6개 동시)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_yahoo_price, s): s for s in symbols}
        for fut in as_completed(futures):
            data = fut.result()
            results[data["ticker"]] = data

    return jsonify({
        "quotes": results,
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # 로컬 테스트용
    app.run(host="0.0.0.0", port=5000, debug=True)
