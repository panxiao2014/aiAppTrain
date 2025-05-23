from typing import List, Dict
import requests
from datetime import datetime, timedelta
from utils.logUtil import setup_logger
from utils.httpUtil import get_http_request

logger = setup_logger("newsUtil")

with open('credentials/newsapi.txt', 'r') as f:
    newsApibKey = f.read().strip()


def get_news_sources() -> None:
    url = "https://newsapi.org/v2/sources"

    params = {
    "apiKey": newsApibKey,

    }

    response = requests.get(url, params=params).json()['sources']
    for item in response:
        print(f"{item['id']}")



def get_past_news(ticker: str, company: str, pastDays: int) -> List[Dict[str, str]]:
    """
    Retrieves a list of news articles about a company based on the ticker and company name
    published in the past 'pastDays' days.

    Args:
    ticker (str): The ticker symbol of the company.
    company (str): The name of the company.
    pastDays (int): The number of days in the past to retrieve news from.

    Returns:
    List[Dict[str, str]]: A list of dictionaries, each containing a date (str, in format 'YYYY-MM-DD')
    and a news article (str).
    """
    url = "https://newsapi.org/v2/everything"

    startDate = (datetime.now() - timedelta(days=pastDays)).strftime("%Y-%m-%d")
    endDate = datetime.now().strftime("%Y-%m-%d")

    qStr = f"{ticker} OR ({company})"

    params = {
    "q": qStr,
    "from": startDate,
    "to": endDate,
    "sortBy": "publishedAt",
    "apiKey": newsApibKey,
    "language": "en",
    "searchIn": "description",
    "page": 1
    }

    try:
        httpData = get_http_request(url=url, params=params)

    except Exception as e:
        logger.warning(f"Something went wrong: {e}")
        return []
    
    if(httpData == None):
        logger.warning(f"Something went wrong")
        return []
    
    newsList = []
    articles = httpData['articles']
    for article in articles:
        newsList.append({"date": article["publishedAt"][0:10], "news": article["description"]})

    logger.info(f"Get {len(newsList)} originnal news")
    return newsList


if __name__ == "__main__":
    newsList = get_past_news("TSM", "Taiwan Semiconductor Manufacturing", 10)
    for news in newsList:
        print(f"Date: {news['date']}")
        print(f"News: {news['news']}")
        print("\n")

    #get_news_sources()
