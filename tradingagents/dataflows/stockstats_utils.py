import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
import logging
from datetime import datetime
from .config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
        data_dir: Annotated[
            str,
            "directory where the stock data is stored.",
        ],
        online: Annotated[
            bool,
            "whether to use online tools to fetch data or offline tools. If True, will use online tools.",
        ] = False,
    ):
        start_time = datetime.now()
        print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting stockstats request: symbol={symbol}, indicator={indicator}, date={curr_date}, online={online}")
        logger.info(f"get_stock_stats called with symbol={symbol}, indicator={indicator}, curr_date={curr_date}, online={online}")
        
        df = None
        data = None
        data_source = "unknown"

        if not online:
            try:
                csv_file_path = os.path.join(
                    data_dir,
                    f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                )
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to read local CSV: {csv_file_path}")
                logger.info(f"Reading local CSV file: {csv_file_path}")
                
                data = pd.read_csv(csv_file_path)
                df = wrap(data)
                data_source = "local_csv"
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully loaded data from local CSV, shape: {data.shape}")
                logger.info(f"Successfully loaded local CSV data with shape: {data.shape}")
                
            except (FileNotFoundError, pd.errors.ParserError) as e:
                if isinstance(e, pd.errors.ParserError):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: CSV parsing error for {symbol}, falling back to online data: {str(e)}")
                    logger.warning(f"CSV parsing error for {symbol}: {str(e)}")
                    # Fall back to online mode when CSV is corrupted
                    online = True
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Local CSV file not found: {csv_file_path}")
                    logger.error(f"Local CSV file not found: {csv_file_path}")
                    raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
        
        if online:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using online mode to fetch data for {symbol}")
            logger.info(f"Switching to online mode for {symbol}")
            
            # Get today's date as YYYY-mm-dd to add to cache
            today_date = pd.Timestamp.today()
            curr_date = pd.to_datetime(curr_date)

            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data range: {start_date} to {end_date}")
            logger.info(f"Data date range: {start_date} to {end_date}")

            # Get config and ensure cache directory exists
            config = get_config()
            os.makedirs(config["data_cache_dir"], exist_ok=True)

            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-YFin-data-{start_date}-{end_date}.csv",
            )

            # Also check if we need to overwrite the corrupted file in data_dir
            corrupted_file = os.path.join(
                data_dir,
                f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )

            try:
                if os.path.exists(data_file):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found existing cache file: {data_file}")
                    logger.info(f"Loading data from cache file: {data_file}")
                    
                    try:
                        data = pd.read_csv(data_file)
                        data["Date"] = pd.to_datetime(data["Date"])
                        data_source = "cache"
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully loaded data from cache, shape: {data.shape}")
                        logger.info(f"Successfully loaded cache data with shape: {data.shape}")
                    except pd.errors.ParserError as cache_error:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: Cache file corrupted, re-downloading: {str(cache_error)}")
                        logger.warning(f"Cache file corrupted for {symbol}: {str(cache_error)}")
                        # Remove corrupted cache file and download fresh data
                        os.remove(data_file)
                        data = yf.download(
                            symbol,
                            start=start_date,
                            end=end_date,
                            multi_level_index=False,
                            progress=False,
                            auto_adjust=True,
                        )
                        data = data.reset_index()
                        data.to_csv(data_file, index=False)
                        data_source = "yahoo_finance_after_cache_error"
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Re-downloaded and cached data after cache error, shape: {data.shape}")
                        logger.info(f"Re-downloaded fresh data after cache error with shape: {data.shape}")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Downloading fresh data from Yahoo Finance...")
                    logger.info(f"Downloading fresh data for {symbol} from Yahoo Finance")
                    data = yf.download(
                        symbol,
                        start=start_date,
                        end=end_date,
                        multi_level_index=False,
                        progress=False,
                        auto_adjust=True,
                    )
                    data = data.reset_index()
                    data.to_csv(data_file, index=False)
                    data_source = "yahoo_finance"
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Downloaded and cached data, shape: {data.shape}")
                    logger.info(f"Downloaded fresh data with shape: {data.shape}")

                # If we fell back to online due to corrupted data, overwrite the corrupted file
                if os.path.exists(corrupted_file):
                    try:
                        # Test if the corrupted file can be read
                        pd.read_csv(corrupted_file)
                    except pd.errors.ParserError:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Overwriting corrupted file: {corrupted_file}")
                        logger.info(f"Overwriting corrupted file: {corrupted_file}")
                        # Ensure the directory exists
                        os.makedirs(os.path.dirname(corrupted_file), exist_ok=True)
                        data.to_csv(corrupted_file, index=False)

                df = wrap(data)
                df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
                curr_date = curr_date.strftime("%Y-%m-%d")
                
            except Exception as download_error:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error downloading data for {symbol}: {str(download_error)}")
                logger.error(f"Error downloading data for {symbol}: {str(download_error)}")
                raise Exception(f"Failed to download fresh data for {symbol}: {str(download_error)}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Calculating indicator '{indicator}' for date {curr_date}")
        logger.info(f"Calculating indicator '{indicator}' for {curr_date}")
        
        df[indicator]  # trigger stockstats to calculate the indicator
        matching_rows = df[df["Date"].str.startswith(curr_date)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully retrieved {indicator}={indicator_value} for {symbol} on {curr_date}")
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Request completed in {duration:.2f}s using data_source='{data_source}'")
            logger.info(f"Successfully calculated {indicator}={indicator_value} for {symbol} on {curr_date}, duration={duration:.2f}s, source={data_source}")
            
            return indicator_value
        else:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result = "N/A: Not a trading day (weekend or holiday)"
            
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] No trading data found for {symbol} on {curr_date}")
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Request completed in {duration:.2f}s, returning: {result}")
            logger.info(f"No trading data for {symbol} on {curr_date}, duration={duration:.2f}s, result={result}")
            
            return result
