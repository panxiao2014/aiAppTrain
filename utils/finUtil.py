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
        logger.warn(f"Something went wrong: {e}")
        return None
    
    #check if httpData has a key 'Information':
    if(httpData['Information']):
        #check if the value contains 'rate limit':
        if('rate limit' in httpData['Information']):
            logger.warn(f"{httpData['Information']}")
            return None
    
    dailyData = httpData['Time Series (Daily)'].get(date)
    if(dailyData):
        return (dailyData["4. close"])
    else:
        return None



# Usage
if __name__ == "__main__":
    #print(get_stock_quote('AAPL'))

    print(get_stock_price('TSM', '2025-05-20'))
