import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from typing import Optional, Dict, Any
from utils.logUtil import setup_logger

logger = setup_logger("httpUtil")


def get_http_request(url: str, params: Optional[dict] = None) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(url, params=params if params is not None else {})
        response.raise_for_status()

        try:
            httpData = response.json()
        except ValueError as e:
            logger.warn("Invalid JSON in response:", e)
            return None

    except HTTPError as e:
        logger.warn(f"HTTP Error: {e} (Status Code: {response.status_code}) (Server Response: {response.text})")
        return None

    except ConnectionError:
        logger.warn("Failed to connect to the server. Check your network or URL.")
        return None

    except Timeout:
        logger.warn(f"Request timed out.")
        return None

    except RequestException as e:
        logger.warn(f"Unexpected request failure: {e}")
        return None

    except Exception as e:
        logger.warn(f"Something went wrong: {e}")
        return None

    return httpData