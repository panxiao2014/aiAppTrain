from typing import List, Dict
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from datetime import datetime, timedelta

with open('credentials/newsapi.txt', 'r') as f:
    newsApibKey = f.read().strip()


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
        response = requests.get(url, params=params)
        response.raise_for_status()

        try:
            articles = response.json()['articles']
        except ValueError as e:
            print("get_past_news: Invalid JSON in response:", e)
            return []

    except HTTPError as e:
        print(f"get_past_news: HTTP Error: {e} (Status Code: {response.status_code}) (Server Response: {response.text})")
        return []

    except ConnectionError:
        print("get_past_news: Failed to connect to the server. Check your network or URL.")
        return []

    except Timeout:
        print(f"get_past_news: Request timed out.")
        return []

    except RequestException as e:
        print(f"get_past_news: Unexpected request failure: {e}")
        return []

    except Exception as e:
        print(f"get_past_news: Something went wrong: {e}")
        return []

    newsList = []
    for article in articles:
        newsList.append({"date": article["publishedAt"][0:10], "news": article["description"]})

    return newsList

if __name__ == "__main__":
    newsList = get_past_news("TSM", "Taiwan Semiconductor Manufacturing", 10)
    for news in newsList:
        print(f"Date: {news['date']}")
        print(f"News: {news['news']}")
        print("\n")
