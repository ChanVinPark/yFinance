from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd

app = FastAPI()

@app.get("/y-finance")
async def get_detailed_financials(ticker: str = Query(..., description="Yahoo Finance ticker (e.g., AAPL, 005930.KS)")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials

        def extract_year_metric(df, metric_name, year):
            if df.empty or metric_name not in df.index:
                return "N/A"
            for col in df.columns:
                if str(year) in str(col):
                    val = df.loc[metric_name, col]
                    return int(val) if pd.notna(val) else "N/A"
            return "N/A"

        def safe_divide(numerator, denominator):
            if isinstance(numerator, (int, float)) and isinstance(denominator, (int, float)) and denominator != 0:
                return round(numerator / denominator, 2)
            return "N/A"

        result = {
            "ticker": ticker,
            "short_name": info.get("shortName", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "enterprise_value": info.get("enterpriseValue", "N/A")
        }

        # TTM — from `info`
        ttm_ebitda = info.get("ebitda", "N/A")
        ttm_revenue = info.get("totalRevenue", "N/A")
        ttm_net_income = info.get("netIncomeToCommon", "N/A")
        ttm_ev_ebitda = safe_divide(result["enterprise_value"], ttm_ebitda)
        ttm_pe_ratio = safe_divide(result["market_cap"], ttm_net_income)
        ttm_margin = safe_divide(ttm_ebitda, ttm_revenue)

        result.update({
            "ebitda_ttm": ttm_ebitda,
            "revenue_ttm": ttm_revenue,
            "net_income_ttm": ttm_net_income,
            "ev_ebitda_ttm": ttm_ev_ebitda,
            "pe_ratio_ttm": ttm_pe_ratio,
            "ebitda_margin_ttm": ttm_margin
        })

        # Historical years
        for year in ["2024", "2023", "2022"]:
            ebitda = extract_year_metric(financials, "EBITDA", year)
            revenue = extract_year_metric(financials, "Total Revenue", year)

            # Net Income fallback
            net_income = "N/A"
            for label in [
                "Net Income", "Net Income Applicable To Common Shares",
                "Consolidated Net Income", "NetIncome",
                "Net Income From Continuing Ops"
            ]:
                net_income = extract_year_metric(financials, label, year)
                if net_income != "N/A":
                    break

            result[f"ebitda_{year}"] = ebitda
            result[f"revenue_{year}"] = revenue
            result[f"net_income_{year}"] = net_income
            result[f"ev_ebitda_{year}"] = safe_divide(result["enterprise_value"], ebitda)
            result[f"pe_ratio_{year}"] = safe_divide(result["market_cap"], net_income)
            result[f"ebitda_margin_{year}"] = safe_divide(ebitda, revenue)

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
