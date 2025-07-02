from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd

app = FastAPI()

# Optional logger for available metric names
def log_available_metrics(financials_df, ticker):
    if financials_df.empty:
        print(f"[DEBUG] No financials found for {ticker}")
        return
    print(f"[DEBUG] Available metrics for {ticker}:")
    for idx in financials_df.index.tolist():
        print(f" - {idx}")

@app.get("/y-finance")
async def get_financials(ticker: str = Query(..., description="Ticker symbol (e.g., AAPL, 005930.KS)")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials

        # Optional debug log
        log_available_metrics(financials, ticker)

        result = {
            "ticker": ticker,
            "short_name": info.get("shortName", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "fiscal_year": "2024"
        }

        # Metric extraction helper
        def extract_metric(df, metric_name):
            if df.empty or metric_name not in df.index:
                return "N/A"
            series = df.loc[metric_name]
            for col in series.index:
                if "2024" in str(col):
                    return int(series[col]) if pd.notna(series[col]) else "N/A"
            return int(series.iloc[0]) if pd.notna(series.iloc[0]) else "N/A"

        # Standard metrics
        result["revenue_2024"] = extract_metric(financials, "Total Revenue")
        result["gross_profit_2024"] = extract_metric(financials, "Gross Profit")
        result["operating_income_2024"] = extract_metric(financials, "Operating Income")
        result["ebitda_2024"] = extract_metric(financials, "EBITDA")

        # Net income with fallback options
        net_income_labels = [
            "Net Income",  # Preferred
            "Net Income Applicable To Common Shares",
            "Consolidated Net Income",
            "NetIncome",
            "Net Income From Continuing Ops"
        ]

        net_income_value = "N/A"
        for label in net_income_labels:
            net_income_value = extract_metric(financials, label)
            if net_income_value != "N/A":
                break

        result["net_income_2024"] = net_income_value

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
