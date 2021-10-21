import requests
from twilio.rest import Client
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

#Alpha Vantage // https://www.alphavantage.co/
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API = os.getenv("STOCK_API")

#NewsAPI // https://www.alphavantage.co/
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API = os.getenv("NEWS_API")

#Twilio // https://console.twilio.com/
account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
from_phone_number = os.getenv("from_phone_number")
to_phone_number = os.getenv("to_phone_number")

yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
day_before = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API
}

stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
tesla_data = stock_response.json()

closing_stock_yesterday = float(tesla_data["Time Series (Daily)"][yesterday]["4. close"])
closing_stock_day_before = float(tesla_data["Time Series (Daily)"][day_before]["4. close"])

stock_difference = closing_stock_day_before - closing_stock_yesterday
up_down = None
if stock_difference > 0:
    up_down = "⏫"
else:
    up_down = "⏬"

diff_percent = round((stock_difference / closing_stock_day_before) * 100)
print(diff_percent)

if abs(diff_percent) >= 0:
    news_param = {
        "qInTitle": COMPANY_NAME,
        "apiKey": NEWS_API,
    }

    news_response = requests.get(NEWS_ENDPOINT, news_param)
    news_response.raise_for_status()
    news_data = news_response.json()

    news_slice = news_data["articles"][:3]
    formatted_articles = [f'{STOCK}: {up_down}{diff_percent}%\nHeadline: {article["title"]}. \nBrief: {article["description"]}' for article in news_slice]

    client = Client(account_sid, auth_token)
    for article in formatted_articles:
        message = client.messages \
            .create(
            body=article,
            from_=from_phone_number,
            to=to_phone_number
        )
        print(message.status)
