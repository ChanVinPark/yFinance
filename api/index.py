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
        financials = stock.financials

        result = {
            "ticker": ticker,
            "short_name": info.get("shortName", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "fiscal_year": "2024"
        }

        # Helper function to extract 2024 value or fallback to latest
        def extract_metric(df, metric_name):
            if df.empty or metric_name not in df.index:
                return "N/A"
            series = df.loc[metric_name]
            for col in series.index:
                if "2024" in str(col):
                    return int(series[col]) if pd.notna(series[col]) else "N/A"
            # fallback: return most recent if 2024 not found
            return int(series.iloc[0]) if pd.notna(series.iloc[0]) else "N/A"

        result["revenue_2024"] = extract_metric(financials, "Total Revenue")
        result["gross_profit_2024"] = extract_metric(financials, "Gross Profit")
        result["operating_income_2024"] = extract_metric(financials, "Operating Income")
        result["ebitda_2024"] = extract_metric(financials, "EBITDA")
        result["net_income_2024"] = extract_metric(financials, "Net Income Applicable To Common Shares")

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
