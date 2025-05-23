import os
from typing import Optional, Tuple
import requests
import finnhub
from utils.httpUtil import get_http_request
from utils.logUtil import setup_logger

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
        logger.warning(f"Could not find stock price for {symbol} on {previousWorkdayData}")
        previousWorkdayData = None
    else:
        previousWorkdayData = previousWorkdayData["4. close"]

    if(workdayData and previousWorkdayData):
        logger.warning(f"Getting price for {symbol} on {workday} and {previousWorkday}: {workdayData}, {previousWorkdayData}")

    return (workdayData, previousWorkdayData)



# Usage
if __name__ == "__main__":
    #print(get_stock_quote('AAPL'))

    print(get_stock_prices('TSM', '2025-05-20', '2025-05-19'))
