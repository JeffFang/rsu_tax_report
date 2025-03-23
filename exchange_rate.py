import requests
import warnings
from datetime import datetime, timedelta
from urllib3.exceptions import NotOpenSSLWarning

# Ignore the NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

def get_exchange_rate(date_str):
    print(f"Fetching exchange rate for {date_str}")
    # Parse input date (MM-DD-YYYY)
    date_obj = datetime.strptime(date_str, "%m-%d-%Y")
    
    # Check if date is in the future
    if date_obj > datetime.now():
        raise ValueError(f"Date {date_str} is in the future. No exchange rate available.")
    
    # Calculate first and last day of the month
    first_day = date_obj.replace(day=1).strftime("%Y-%m-%d")
    last_day = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    last_day = last_day.strftime("%Y-%m-%d")
    
    # Fetch data for the entire month
    url = f"https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date={first_day}&end_date={last_day}"
    print(f"url: {url}")
    response = requests.get(url).json()
    
    # Check for valid response
    if "observations" not in response or len(response["observations"]) == 0:
        raise ValueError(f"No exchange rate data found for {date_str} or its month.")
    
    # Find the rate for the exact date
    target_date = date_obj.strftime("%Y-%m-%d")
    for observation in response["observations"]:
        if observation["d"] == target_date:
            return float(observation["FXUSDCAD"]["v"])
    
    # If exact date not found, use the latest available date in the month
    latest_observation = response["observations"][-1]
    print(f"Using nearest rate from {latest_observation['d']}")
    return float(latest_observation["FXUSDCAD"]["v"])