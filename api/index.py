from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd

app = FastAPI()

@app.get("/y-finance")
async def get_financials(ticker: str = Query(..., description="Ticker symbol (e.g., AAPL, 005930.KS)")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap", "N/A")
        short_name = info.get("shortName", "N/A")

        # Get historical financials (income statement)
        financials = stock.financials
        if financials.empty or "EBITDA" not in financials.index:
            ebitda_2024 = "N/A"
        else:
            ebitda_series = financials.loc["EBITDA"]
            # Try to get 2024 specifically
            ebitda_2024 = None
            for col in ebitda_series.index:
                if "2024" in str(col):
                    ebitda_2024 = ebitda_series[col]
                    break
            # If 2024 not found, fallback to latest
            if ebitda_2024 is None:
                ebitda_2024 = ebitda_series.iloc[0]

        return {
            "ticker": ticker,
            "short_name": short_name,
            "market_cap": market_cap,
            "ebitda_2024": None if pd.isna(ebitda_2024) else int(ebitda_2024)
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
