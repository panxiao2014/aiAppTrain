import os
import json
from prettytable import PrettyTable
from typing import Optional, Tuple
import requests
import finnhub
from utils.httpUtil import get_http_request
from utils.logUtil import setup_logger
from utils.cacheUtil import CacheUtil, StockNewsKeyGenerator

logger = setup_logger("finUtil")


with open('credentials/finnhub.txt', 'r') as f:
    finnhubKey = f.read().strip()
    finnhubClient = finnhub.Client(api_key=finnhubKey)

with open('credentials/alpha.vantage.txt', 'r') as f:
    alphaVantageKey = f.read().strip()



def get_company_list() -> list:
    #check if data/tickers.csv exists
    if os.path.exists('data/tickers.csv'):
        pass
    else:
        with open("credentials/alpha.vantage.txt", "r") as f:
            alpha_vantage_key = f.read().strip()
        url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={alpha_vantage_key}"

        response = requests.get(url)
        data = response.text

        logger.info(f"Save ticker list to data/tickers.csv")

        #save first and second columns of data to a csv file in data folder
        with open("data/tickers.csv", "w") as f:
            for line in data.splitlines():
                f.write(",".join(line.split(",")[:2]) + "\n")

    companyList = []
    with open("data/tickers.csv", "r") as f:
        next(f) #skip the first line
        for line in f:
            companyList.append(line.strip().split(","))

    return companyList
    

def get_stock_quote(symbol: str) -> float:
    return finnhubClient.quote(symbol)['c']


def get_stock_price(symbol: str, date: str) -> Optional[Tuple[float, float]]:
    """
    Get the stock price for a given symbol and date.

    Args:
        symbol (str): The stock symbol.
        date (str): The date in the format 'YYYY-MM-DD'.

    Returns:
        A float of the close price of the stock
        on the given date. If the date is not available, returns None.
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={alphaVantageKey}"
    try:
        httpData = get_http_request(url=url)
    except Exception as e:
        logger.warning(f"Something went wrong: {e}")
        return None
    
    #check if httpData has a key 'Information':
    if('Information' in httpData):
        #check if the value contains 'rate limit':
        if('rate limit' in httpData['Information']):
            logger.warning(f"{httpData['Information']}")
            return None
    
    dailyData = httpData['Time Series (Daily)'].get(date)
    if(dailyData):
        logger.info(f"Getting stock price for {symbol} on {date}, price: {dailyData}")
        return (dailyData["4. close"])
    else:
        logger.warning(f"Could not find stock price for {symbol} on {date}")
        return None
    

def get_stock_prices(symbol: str, workday: str, previousWorkday: str) -> Tuple[Optional[float], Optional[float]]:
    """
    For a given stock symbol, get the stock price on the given date and price on the previous workday.

    Args:
        symbol (str): The stock symbol.
        workday (str): The date in the format 'YYYY-MM-DD'.
        previousWorkday (str): The date in the format 'YYYY-MM-DD'.

    Returns:
        A tuple of float of the close price of the stock
        on the given date and the previous day.
        If the price is not available, set it to None.
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={alphaVantageKey}"
    try:
        httpData = get_http_request(url=url)
    except Exception as e:
        logger.warning(f"Something went wrong: {e}")
        return None
    
    #check if httpData has a key 'Information':
    if('Information' in httpData):
        #check if the value contains 'rate limit':
        if('rate limit' in httpData['Information']):
            logger.warning(f"{httpData['Information']}")
            return (None, None)
    
    workdayData = httpData['Time Series (Daily)'].get(workday)
    previousWorkdayData = httpData['Time Series (Daily)'].get(previousWorkday)

    if(not workdayData):
        logger.warning(f"Could not find stock price for {symbol} on {workday}")
        workdayData = None
    else:
        workdayData = workdayData["4. close"]
    if(not previousWorkdayData):
        logger.warning(f"Could not find stock price for {symbol} on {previousWorkday}")
        previousWorkdayData = None
    else:
        previousWorkdayData = previousWorkdayData["4. close"]

    if(workdayData and previousWorkdayData):
        logger.info(f"Getting price for {symbol} on {workday} and {previousWorkday}: {workdayData}, {previousWorkdayData}")

    return (workdayData, previousWorkdayData)


def format_stock_event_string(stockEvent: str) -> PrettyTable:
    """
    For a stock event representd in json format string, format it to a table.

    Args:
        stockEvent(str) : The stock event representd in json format string. It has the following format:
            {{
            "stock_symbol": companyTicker,
            "past_days": pastDays,
            "stock_total_events": total_number,
            "stock_price_events": [
                {{
                "time": "yyyy-mm-dd",
                "summary": "brief summary of the event",
                "previous": "the stock price of the previous workday. If price is not available, return None",
                "close": "the stock price of the closest workday. If price is not available, return None"
                }}
            ]
            }}

    Returns:
        A formatted table of the stock event
    """
    #get the json format string
    stockEvent = json.loads(stockEvent)

    logger.info(f"Formatting stock event string: {stockEvent}")

    #get the stock price events
    stock_price_events = stockEvent["stock_price_events"]

    #sort the stock price events by time
    stock_price_events.sort(key=lambda x: x["time"])

    #format the list of events into a table, the table has four columns: time, summary, previous, close
    table = PrettyTable()
    table.field_names = ["Time", "Summary", "Previous", "Close"]
    table._max_width = {"Summary": 50}  # set the max width of "summary" column to 50
    table.hrules = True  # enable horizontal rules
    table.wrap_lines = True  # enable auto wrap of long string
    table.align["Summary"] = "l"  # align "summary" column to left
    for event in stock_price_events:
        table.add_row([event["time"], event["summary"], event["previous"], event["close"]])

    print(table)
    return table


async def save_stock_event_to_cache(stockEvent: str):
    """
    For a stock event representd in json format string, save it to a cache file.

    Args:
        stockEvent(str) : The stock event representd in json format string. It has the following format:
            {{
            "stock_symbol": companyTicker,
            "past_days": pastDays,
            "stock_total_events": total_number,
            "stock_price_events": [
                {{
                "time": "yyyy-mm-dd",
                "summary": "brief summary of the event",
                "previous": "the stock price of the previous workday. If price is not available, return None",
                "close": "the stock price of the closest workday. If price is not available, return None"
                }}
            ]
            }}
    """
    stockEvent = json.loads(stockEvent)

    #if stock_price_events is empty, then don't save to cache:
    if(len(stockEvent["stock_price_events"]) == 0):
        return
    
    #save to cache:
    stock_symbol = stockEvent["stock_symbol"]
    past_days = stockEvent["past_days"]
    keyGenerator = StockNewsKeyGenerator()
    stockNewsCache = CacheUtil(100, 'data/stockNewsCache.json', keyGenerator)
    await stockNewsCache.load_cache()

    await stockNewsCache.add(stockEvent, stock_symbol, past_days)
    logger.info(f"Added stock news to cache by: {stock_symbol}, {past_days}")
    return



# Usage
if __name__ == "__main__":
    #print(get_stock_quote('AAPL'))

    #print(get_stock_prices('TSM', '2025-05-20', '2025-05-19'))

    event_string = """ {"stock_total_events":1,"stock_price_events":[{"time":"2025-05-23","summary":"Oracle will reportedly buy $40 billion worth of Nvidia chips to power the first Stargate project, a new data center in Abilene, Texas. The company will buy 400,000 of Nvidia latest 'superchips' for training and running artificial intelligence (AI) systems...","previous":"132.8300","close":"131.2900"}]}"""

    table = format_stock_event_string(event_string)
    print(table)
