"""
Crossfit Potrero Hill Scraper

Find the latest workout at Crossfit Potrero Hill
"""

import urllib.request
import argparse
import os
from datetime import date, timedelta
from bs4 import BeautifulSoup


def format_date(delay=0):
    """
    Format date for wod blog

    Delay is how many days ago, default 0 (today)
    """

    day = date.today() - timedelta(delay)
    weekday = day.strftime("%A").lower()

    # NOTE: Month abbreviations are inconsistent. October and November are 3
    # chars (oct, nov) while September is 4 chars (sept). Unsure of others but
    # will default to 3 chars
    abbreviation_len = 3
    if day.month == 9:
        abbreviation_len = 4
    month = day.strftime("%B")[:abbreviation_len].lower()

    # NOTE: Post date is usually one before WOD date
    post_day = day - timedelta(1)
    post_date = post_day.strftime("%Y/%m/%d")

    post_title = "/wod-%s-%s-%s/" % (weekday, month, day.day)

    return post_date + post_title


def get_content(date):
    """
    Get the content of the WOD blog for a given date
    """

    base_url = "http://crossfitph.com/"
    crossfit_ph_url = base_url + date

    req = urllib.request.Request(
        crossfit_ph_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    page = response.read()

    return (crossfit_ph_url, page)


def format_content(page):
    """
    Parse and format the content of the html page
    """

    # Isolate WOD Text
    soup = BeautifulSoup(page, "html.parser")
    text = soup.get_text()

    beginning_split = text.split("FAQ")
    relevant = beginning_split[1]
    middle_split = relevant.split("Athlete of the")
    relevant = middle_split[0]

    # Clean up
    lines = relevant.splitlines()
    lines = [line.strip() for line in lines if line]
    lines = lines[4:]

    # Format
    HEADERS = ["Strength A:", "Strength B:", "Strength:", "WOD:", "Skill:",
               "Warm:", "Finisher:", "9:30 and 10:30 am Regular CrossFit"]

    # Add contents as bullets
    wod_text = ""
    for line in lines:
        prefix = "  - "
        if line in HEADERS:
            prefix = "- "
        line = prefix + line
        wod_text += line + "\n"

    return wod_text


def main():
    """
    Implement helper functions
    """

    # Configure arguments
    parser = argparse.ArgumentParser(description="Get Workout at Crossfit-PH")
    parser.add_argument(
        "delay",
        metavar="D",
        type=int,
        nargs="?",
        default="0",
        help="How many days ago was the workout (today would be 0)")
    args = parser.parse_args()
    delay = args.delay

    # Run helper functions with configured args
    date = format_date(delay)
    try:
        url, content = get_content(date)
        text = format_content(content)
        print(text)
        print("Scraped from: \n{}".format(url))

        # Copy to clipboard
        os.system("echo '%s' | pbcopy" % text)
    except urllib.error.HTTPError:
        print("ERROR: Couldn't find URL:\n%s" % "http://crossfitph.com/" +
              date)
    except urllib.error.URLError:
        print("ERROR: No internet connection")


if __name__ == "__main__":
    main()
