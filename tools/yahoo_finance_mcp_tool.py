"""
Yahoo Finance MCP Tool implementation
"""
import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool
import pandas as pd


class YahooFinanceMCPTool(BaseMCPTool):
    """MCP Tool for Yahoo Finance operations"""

    def _initialize(self):
        """Initialize Yahoo Finance specific components"""
        # Yahoo Finance doesn't require API keys
        pass

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Yahoo Finance tool calls

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            # Map tool names to methods
            tool_methods = {
                "get_stock_price": self._get_stock_price,
                "get_stock_info": self._get_stock_info,
                "get_historical_data": self._get_historical_data,
                "get_financials": self._get_financials,
                "get_balance_sheet": self._get_balance_sheet,
                "get_cash_flow": self._get_cash_flow,
                "get_dividends": self._get_dividends,
                "get_splits": self._get_splits,
                "get_recommendations": self._get_recommendations,
                "get_institutional_holders": self._get_institutional_holders,
                "get_options": self._get_options,
                "get_news": self._get_news,
                "get_earnings": self._get_earnings,
                "get_actions": self._get_actions,
                "search_symbols": self._search_symbols,
                "get_market_summary": self._get_market_summary,
                "get_trending_tickers": self._get_trending_tickers,
                "get_sector_performance": self._get_sector_performance
            }

            if tool_name in tool_methods:
                result = tool_methods[tool_name](arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    def _get_stock_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current stock price"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "price": info.get('currentPrice', info.get('regularMarketPrice')),
                "currency": info.get('currency', 'USD'),
                "change": info.get('regularMarketChange'),
                "change_percent": info.get('regularMarketChangePercent'),
                "previous_close": info.get('previousClose'),
                "open": info.get('open'),
                "day_high": info.get('dayHigh'),
                "day_low": info.get('dayLow'),
                "volume": info.get('volume'),
                "market_cap": info.get('marketCap'),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_stock_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive stock information"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract key information
            return {
                "symbol": symbol,
                "company_name": info.get('longName'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "country": info.get('country'),
                "website": info.get('website'),
                "description": info.get('longBusinessSummary'),
                "employees": info.get('fullTimeEmployees'),
                "market_cap": info.get('marketCap'),
                "enterprise_value": info.get('enterpriseValue'),
                "trailing_pe": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "peg_ratio": info.get('pegRatio'),
                "price_to_book": info.get('priceToBook'),
                "price_to_sales": info.get('priceToSalesTrailing12Months'),
                "profit_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                "return_on_equity": info.get('returnOnEquity'),
                "return_on_assets": info.get('returnOnAssets'),
                "revenue": info.get('totalRevenue'),
                "revenue_per_share": info.get('revenuePerShare'),
                "earnings_growth": info.get('earningsGrowth'),
                "revenue_growth": info.get('revenueGrowth'),
                "gross_margins": info.get('grossMargins'),
                "ebitda_margins": info.get('ebitdaMargins'),
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "book_value": info.get('bookValue'),
                "cash": info.get('totalCash'),
                "debt": info.get('totalDebt'),
                "beta": info.get('beta'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "50_day_average": info.get('fiftyDayAverage'),
                "200_day_average": info.get('twoHundredDayAverage'),
                "dividend_rate": info.get('dividendRate'),
                "dividend_yield": info.get('dividendYield'),
                "ex_dividend_date": info.get('exDividendDate'),
                "payout_ratio": info.get('payoutRatio')
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_historical_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical price data"""
        symbol = params.get('symbol', '').upper()
        period = params.get('period', '1mo')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval = params.get('interval', '1d')  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                hist = ticker.history(period=period, interval=interval)

            # Convert to list of dictionaries
            data = []
            for index, row in hist.iterrows():
                data.append({
                    "date": index.strftime('%Y-%m-%d'),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })

            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data_points": len(data),
                "data": data
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_financials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial statements"""
        symbol = params.get('symbol', '').upper()
        quarterly = params.get('quarterly', False)

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            if quarterly:
                financials = ticker.quarterly_financials
            else:
                financials = ticker.financials

            if financials.empty:
                return {"symbol": symbol, "data": {}, "message": "No financial data available"}

            # Convert to dictionary format
            data = {}
            for col in financials.columns:
                col_data = {}
                for idx in financials.index:
                    value = financials.loc[idx, col]
                    col_data[idx] = float(value) if pd.notna(value) else None
                data[col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col)] = col_data

            return {
                "symbol": symbol,
                "frequency": "quarterly" if quarterly else "annual",
                "data": data
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_balance_sheet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get balance sheet data"""
        symbol = params.get('symbol', '').upper()
        quarterly = params.get('quarterly', False)

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            if quarterly:
                balance_sheet = ticker.quarterly_balance_sheet
            else:
                balance_sheet = ticker.balance_sheet

            if balance_sheet.empty:
                return {"symbol": symbol, "data": {}, "message": "No balance sheet data available"}

            # Convert to dictionary format
            data = {}
            for col in balance_sheet.columns:
                col_data = {}
                for idx in balance_sheet.index:
                    value = balance_sheet.loc[idx, col]
                    col_data[idx] = float(value) if pd.notna(value) else None
                data[col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col)] = col_data

            return {
                "symbol": symbol,
                "frequency": "quarterly" if quarterly else "annual",
                "data": data
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_cash_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cash flow statement data"""
        symbol = params.get('symbol', '').upper()
        quarterly = params.get('quarterly', False)

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            if quarterly:
                cash_flow = ticker.quarterly_cashflow
            else:
                cash_flow = ticker.cashflow

            if cash_flow.empty:
                return {"symbol": symbol, "data": {}, "message": "No cash flow data available"}

            # Convert to dictionary format
            data = {}
            for col in cash_flow.columns:
                col_data = {}
                for idx in cash_flow.index:
                    value = cash_flow.loc[idx, col]
                    col_data[idx] = float(value) if pd.notna(value) else None
                data[col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col)] = col_data

            return {
                "symbol": symbol,
                "frequency": "quarterly" if quarterly else "annual",
                "data": data
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_dividends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get dividend history"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends.empty:
                return {"symbol": symbol, "dividends": [], "message": "No dividend data available"}

            # Convert to list
            div_list = []
            for date, amount in dividends.items():
                div_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "amount": round(float(amount), 4)
                })

            return {
                "symbol": symbol,
                "dividends": div_list,
                "count": len(div_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_splits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock split history"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits

            if splits.empty:
                return {"symbol": symbol, "splits": [], "message": "No split data available"}

            # Convert to list
            split_list = []
            for date, ratio in splits.items():
                split_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "ratio": f"{ratio}:1"
                })

            return {
                "symbol": symbol,
                "splits": split_list,
                "count": len(split_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get analyst recommendations"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            recs = ticker.recommendations

            if recs is None or recs.empty:
                return {"symbol": symbol, "recommendations": [], "message": "No recommendations available"}

            # Get recent recommendations
            recent_recs = recs.tail(10)

            rec_list = []
            for index, row in recent_recs.iterrows():
                rec_list.append({
                    "date": index.strftime('%Y-%m-%d') if hasattr(index, 'strftime') else str(index),
                    "firm": row.get('Firm', ''),
                    "to_grade": row.get('To Grade', ''),
                    "from_grade": row.get('From Grade', ''),
                    "action": row.get('Action', '')
                })

            return {
                "symbol": symbol,
                "recommendations": rec_list,
                "count": len(rec_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_institutional_holders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get institutional holders information"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            holders = ticker.institutional_holders

            if holders is None or holders.empty:
                return {"symbol": symbol, "holders": [], "message": "No institutional holder data available"}

            # Convert to list
            holder_list = []
            for _, row in holders.iterrows():
                holder_list.append({
                    "holder": row.get('Holder', ''),
                    "shares": int(row.get('Shares', 0)),
                    "value": float(row.get('Value', 0)),
                    "percentage": float(row.get('% Out', 0)) if '% Out' in row else None
                })

            return {
                "symbol": symbol,
                "institutional_holders": holder_list,
                "count": len(holder_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get options chain data"""
        symbol = params.get('symbol', '').upper()
        expiration_date = params.get('expiration_date')

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            # Get available expiration dates
            expirations = ticker.options

            if not expirations:
                return {"symbol": symbol, "options": {}, "message": "No options data available"}

            # Use specified date or first available
            exp_date = expiration_date if expiration_date in expirations else expirations[0]

            # Get options chain
            opt_chain = ticker.option_chain(exp_date)

            # Process calls and puts
            calls_data = []
            for _, row in opt_chain.calls.iterrows():
                calls_data.append({
                    "strike": float(row['strike']),
                    "last_price": float(row['lastPrice']) if pd.notna(row['lastPrice']) else None,
                    "bid": float(row['bid']) if pd.notna(row['bid']) else None,
                    "ask": float(row['ask']) if pd.notna(row['ask']) else None,
                    "volume": int(row['volume']) if pd.notna(row['volume']) else 0,
                    "open_interest": int(row['openInterest']) if pd.notna(row['openInterest']) else 0,
                    "implied_volatility": float(row['impliedVolatility']) if pd.notna(
                        row['impliedVolatility']) else None
                })

            puts_data = []
            for _, row in opt_chain.puts.iterrows():
                puts_data.append({
                    "strike": float(row['strike']),
                    "last_price": float(row['lastPrice']) if pd.notna(row['lastPrice']) else None,
                    "bid": float(row['bid']) if pd.notna(row['bid']) else None,
                    "ask": float(row['ask']) if pd.notna(row['ask']) else None,
                    "volume": int(row['volume']) if pd.notna(row['volume']) else 0,
                    "open_interest": int(row['openInterest']) if pd.notna(row['openInterest']) else 0,
                    "implied_volatility": float(row['impliedVolatility']) if pd.notna(
                        row['impliedVolatility']) else None
                })

            return {
                "symbol": symbol,
                "expiration_date": exp_date,
                "available_expirations": list(expirations),
                "calls": calls_data,
                "puts": puts_data
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_news(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent news for a stock"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return {"symbol": symbol, "news": [], "message": "No news available"}

            # Format news items
            news_list = []
            for item in news[:10]:  # Limit to 10 most recent
                news_list.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "publisher": item.get('publisher', ''),
                    "published": datetime.fromtimestamp(
                        item.get('providerPublishTime', 0)).isoformat() if 'providerPublishTime' in item else '',
                    "type": item.get('type', ''),
                    "uuid": item.get('uuid', '')
                })

            return {
                "symbol": symbol,
                "news": news_list,
                "count": len(news_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_earnings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get earnings data"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)

            # Get earnings dates
            earnings_dates = ticker.earnings_dates
            earnings_hist = ticker.earnings_history

            result = {"symbol": symbol}

            # Process earnings dates if available
            if earnings_dates is not None and not earnings_dates.empty:
                dates_list = []
                for index, row in earnings_dates.head(8).iterrows():
                    dates_list.append({
                        "date": index.strftime('%Y-%m-%d') if hasattr(index, 'strftime') else str(index),
                        "eps_estimate": float(row['EPS Estimate']) if pd.notna(row.get('EPS Estimate')) else None,
                        "eps_actual": float(row['Reported EPS']) if pd.notna(row.get('Reported EPS')) else None
                    })
                result["earnings_dates"] = dates_list

            # Process earnings history if available
            if earnings_hist is not None and len(earnings_hist) > 0:
                hist_list = []
                for item in earnings_hist:
                    hist_list.append({
                        "date": item.get('date', ''),
                        "eps_actual": item.get('epsActual'),
                        "eps_estimate": item.get('epsEstimate')
                    })
                result["earnings_history"] = hist_list

            return result

        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _get_actions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get corporate actions (dividends, splits, etc.)"""
        symbol = params.get('symbol', '').upper()

        if not symbol:
            return {"error": "Symbol is required"}

        try:
            ticker = yf.Ticker(symbol)
            actions = ticker.actions

            if actions.empty:
                return {"symbol": symbol, "actions": [], "message": "No corporate actions available"}

            # Convert to list
            actions_list = []
            for date, row in actions.iterrows():
                action = {"date": date.strftime('%Y-%m-%d')}

                if pd.notna(row.get('Dividends')) and row['Dividends'] > 0:
                    action['type'] = 'dividend'
                    action['amount'] = float(row['Dividends'])

                if pd.notna(row.get('Stock Splits')) and row['Stock Splits'] > 0:
                    action['type'] = 'split'
                    action['ratio'] = float(row['Stock Splits'])

                if 'type' in action:
                    actions_list.append(action)

            return {
                "symbol": symbol,
                "actions": actions_list,
                "count": len(actions_list)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def _search_symbols(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for stock symbols"""
        query = params.get('query', '')

        if not query:
            return {"error": "Query is required"}

        # This is a basic implementation - Yahoo Finance doesn't provide a direct search API
        # In production, you might want to maintain a local database of symbols

        return {
            "query": query,
            "results": [],
            "message": "Symbol search requires additional implementation or data source"
        }

    def _get_market_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get market summary for major indices"""
        indices = params.get('indices', ['^GSPC', '^DJI', '^IXIC', '^RUT'])  # S&P500, Dow, Nasdaq, Russell

        summary = {}

        for index in indices:
            try:
                ticker = yf.Ticker(index)
                info = ticker.info

                summary[index] = {
                    "name": info.get('longName', index),
                    "price": info.get('regularMarketPrice'),
                    "change": info.get('regularMarketChange'),
                    "change_percent": info.get('regularMarketChangePercent'),
                    "previous_close": info.get('previousClose'),
                    "volume": info.get('volume')
                }
            except:
                summary[index] = {"error": "Failed to fetch data"}

        return {"market_summary": summary}

    def _get_trending_tickers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trending tickers"""
        # This would typically require scraping or a different API
        # Providing a placeholder implementation

        return {
            "trending": [],
            "message": "Trending tickers requires additional implementation or data source"
        }

    def _get_sector_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sector performance data"""
        # Define sector ETFs
        sectors = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Consumer Discretionary': 'XLY',
            'Communication': 'XLC',
            'Industrials': 'XLI',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Materials': 'XLB'
        }

        performance = {}

        for sector, etf in sectors.items():
            try:
                ticker = yf.Ticker(etf)
                info = ticker.info

                performance[sector] = {
                    "symbol": etf,
                    "price": info.get('regularMarketPrice'),
                    "change_percent": info.get('regularMarketChangePercent'),
                    "day_high": info.get('dayHigh'),
                    "day_low": info.get('dayLow'),
                    "volume": info.get('volume')
                }
            except:
                performance[sector] = {"error": "Failed to fetch data"}

        return {"sector_performance": performance}