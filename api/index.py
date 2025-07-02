from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf

app = FastAPI()

@app.get("/y-finance")
async def get_financials(ticker: str = Query(..., description="Ticker symbol (e.g., AAPL, 005930.KS)")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "short_name": info.get("shortName", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A")
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
