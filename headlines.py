
import datetime
import json
import urllib2
import urllib
import feedparser
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml', 'cnn': 'http://rss.ccn.com/rss/edition.rss',
           'fox': 'http: //feeds.foxnews.com/foxnews /latest', 'iol': 'http://www.iol.co.za/cmlink/1.640'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cb3823bdd1813a699aa834b14a69cb99"
CURRENCY_URL = "http://openexchangerates.org//api/latest.json?app_id=34e74d481d9d42059001dbf7e93cb513"

DEFAULTS = {
    'publication': 'bbc',
    'city': 'LONDON,UK',
    'currency_from': 'GBP',
    'currency_to': 'USD'}


@app.route("/")

def home():
    publication = request.args.get('publication')
    if not publication:
        publication=request.cookies.get("publicationss")
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']

    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']

    rate,currencies = get_rate(currency_from,currency_to)

    response = make_response (render_template("home.html", articles=articles,
    weather=weather,currency_from=currency_from,
    currency_to=currency_to, rate = rate,currencies = sorted(currencies)))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)
    return response


def get_rate(frm,to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate,parsed.keys())


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication= DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed["entries"]


def get_weather(query):
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cb3823bdd1813a699aa834b14a69cb99'

    query = urllib.quote(query)
    url = api_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather=None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                 "temperature":parsed["main"]["temp"],
                 'city':parsed['name'],
                 'country': parsed['sys']['country']
                 }
    return weather


if __name__=='__main__':
    app.run(port=5000,debug = True)
