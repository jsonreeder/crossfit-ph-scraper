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
    month = day.strftime("%B")[:4].lower()

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

    return page


def format_content(page):
    """
    Parse and format the content of the html page
    """

    # Isolate WOD Text
    soup = BeautifulSoup(page, "html.parser")
    text = soup.get_text()

    pre, relevant = text.split("FAQ")
    relevant, post = relevant.split("WOD LOGGING")

    # Clean up
    lines = relevant.splitlines()
    lines = [line.strip() for line in lines if line]
    lines = lines[2:]

    # Format
    HEADERS = ["Strength A:", "Strength B:", "Strength:", "WOD:", "Skill:",
               "Warm:"]

    # Include title
    wod_text = lines.pop(0) + "\n\n"

    # Ignore by-line
    del lines[0]

    # Add contents as bullets
    for line in lines:
        prefix = "  - "
        if line in HEADERS:
            prefix = "- "
        line = prefix + line
        wod_text += line + "\n"

    return wod_text


if __name__ == "__main__":

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

    date = format_date(delay)
    content = get_content(date)
    text = format_content(content)
    print(text)

    # Copy to clipboard
    os.system("echo '%s' | pbcopy" % text)
