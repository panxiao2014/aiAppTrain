from datetime import datetime, timedelta
from utils.logUtil import setup_logger

logger = setup_logger("timeUtil")

def find_workdays(input_date):
    """
    Given an input date, find the closest workday and the previous workday.
    
    A workday is defined as any day of the week that is not Saturday or Sunday.

    For example:
    1. If input date is Saturday or Sunday, then the closest workday is Friday and the previous workday is Thursday.
    2. If input date is Monday, then the closest workday is Monday and the previous workday is Friday of last week.
    3. Otherwise, the closest workday is the input date itself and the previous workday is the input date minus one day.
    
    Parameters:
        input_date (str): Input date in the form of 'YYYY-MM-DD'.
    
    Returns:
        tuple: A tuple of two strings representing the closest workday and the previous workday, respectively.
    """
    date = datetime.strptime(input_date, "%Y-%m-%d").date()
    day_of_week = date.weekday()  # Monday is 0, Sunday is 6
    
    if day_of_week < 5:  # Monday to Friday
        closest_workday = date
        previous_workday = date - timedelta(days=1)
        while previous_workday.weekday() >= 5:  # if it's Saturday or Sunday
            previous_workday -= timedelta(days=1)
    else:  # Saturday or Sunday
        closest_workday = date - timedelta(days=(day_of_week - 4))  # Saturday (5) -> 1 day back to Friday, Sunday (6) -> 2 days back
        previous_workday = closest_workday - timedelta(days=1)
        while previous_workday.weekday() >= 5:
            previous_workday -= timedelta(days=1)

    closest_workday = closest_workday.strftime('%Y-%m-%d')
    previous_workday = previous_workday.strftime('%Y-%m-%d')

    logger.info(f"find workdays for {input_date}: {closest_workday} {previous_workday}")
    
    return (closest_workday, previous_workday)


if __name__ == "__main__":
    print(find_workdays("2025-05-17"))