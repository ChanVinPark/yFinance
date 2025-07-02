from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from typing import Optional
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Simple mapping for a few KR/EN names to ticker — extend or auto-detect in prod
COMPANY_TICKER_MAP = {
    "삼성전자": "005930.KS",
    "현대차": "005380.KS",
    "LG화학": "051910.KQ",
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Netflix": "NFLX",
    "Tesla": "TSLA"
}

@app.get("/finance")
async def get_financials(company: str = Query(..., description="Company name (EN or KR)")):
    ticker = COMPANY_TICKER_MAP.get(company)
    if not ticker:
        return JSONResponse(content={"error": "Ticker not found. Update the mapping table."}, status_code=400)
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")

        return {
            "company": company,
            "ticker": ticker,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
