from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import csv
import re
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import subprocess
from tqdm import tqdm
import yaml
import numpy as pd

# Function to handle NoSuchElementException
def handle_no_such_element_exception(data_extraction_task):
    """
    Safely find an element, returning None if not found
    
    :param data_extraction_task: A lambda function that attempts to find an element
    :return: Element value or None if not found
    """
        
    try:
        return data_extraction_task()
    except NoSuchElementException:
        return None


# Function to get geolocation data
def get_geolocation(description):
    geolocator = Nominatim(user_agent="geo_app") # Nominatim geocoder for OpenStreetMap data
    location = geolocator.geocode(f"{description}" , timeout=10)
    print(location)
    if location:
        return location.latitude, location.longitude
    return None, None

# Function to try multiple geocoding strategies
def find_location(description):
    # Try the full description first
    latitude, longitude = get_geolocation(description)
    if latitude is not None and longitude is not None:
        return latitude, longitude
    
    # If not found, simplify the description and try again
    simplified_description = description.split(',')[-1].strip()
    return get_geolocation(simplified_description)


def scrape_properties(url, max_button_clicks, data_name, country_short):
    """Function that scrolls down the page, extract information about its properties and 
    clicks 'Load More Results' button."""
    
    # Create a Chrome web driver instance
    driver = webdriver.Chrome(service=Service())

    # Connect to the target page
    driver.get(url)

    # Handle the sign-in alert
    try:
        close_button = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[role=\"dialog\"] button[aria-label=\"Dismiss sign-in info.\"]"))
        )
        close_button.click()
    except Exception:
        print("Sign-in modal did not appear, continuing...")

    # Scroll down the page in a human-like fashion with a maximum scroll time
    scroll_pause_time = 2  # Pause time between scrolls
    max_scroll_time = 320  # Maximum scroll time in seconds
    start_time = time.time()
    last_height = driver.execute_script("return document.body.scrollHeight")
    load_more_button_found = False

    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height or (time.time() - start_time) > max_scroll_time:
            break
        last_height = new_height

        # Check if "Load More Results" button is present and click it
        if max_button_clicks > 0:
            try:
                load_more_button = WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "button.a83ed08757.c21c56c305.bf0537ecb5.f671049264.af7297d90d.c0e0affd09")
                    )
                )
                load_more_button.click()
                load_more_button_found = True
                print("Clicked 'Load More Results' button")
                # Add a small pause after clicking the button
                time.sleep(2)
                max_button_clicks -= 1
            except TimeoutException:
                pass  # Button not yet available, continue scrolling

    # If "Load More Results" button was found, wait an additional time for final loading
    if load_more_button_found:
        time.sleep(4)  # Adjust this wait time as needed

    # Where to store the scraped data
    items = []

    # Select all property items on the page. It finds all elements on the page that have 
    # the data-testid attribute "property-card"
    property_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid=\"property-card\"]")

    print(f"Found {len(property_items)} property items.")

    for property_item in property_items:
        # scraping logic...
        # url: Finds the href attribute of an anchor tag with data-testid "property-card-desktop-single-image"
        url = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "a[data-testid=\"property-card-desktop-single-image\"]").get_attribute("href"))
        # image: Retrieves the src attribute of an img tag with data-testid "image"
        image = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "img[data-testid=\"image\"]").get_attribute("src"))
        # Adds a random delay between 1-2 seconds to avoid rapid scraping
        time.sleep(random.uniform(1, 2))
        # title: Gets the text of an element with data-testid "title"
        title = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"title\"]").text)
        # address: Gets the text of an element with data-testid "address"
        address = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"address\"]").text)
        # distance: Gets the text of an element with data-testid "distance"
        distance = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"distance\"]").text)

        review_score = None
        review_count = None
        # review_text: Gets the text of an element with data-testid "review-score"
        review_text = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"review-score\"]").text)
        if review_text is not None:
            parts = review_text.split("\n")
            for part in parts:
                part = part.strip()
                if part.replace(".", "", 1).isdigit():
                    review_score = float(part)
                elif "reviews" in part:
                    review_count = int(part.split(" ")[0].replace(",", ""))
        
        description = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"recommended-units\"]").text)
        time.sleep(random.uniform(1, 2))
        price_element = handle_no_such_element_exception(lambda: (property_item.find_element(By.CSS_SELECTOR, "[data-testid=\"availability-rate-information\"]")))
        if price_element is not None:
            original_price = handle_no_such_element_exception(lambda: (
                price_element.find_element(By.CSS_SELECTOR, "[aria-hidden=\"true\"]:not([data-testid])").text.replace(",", "")
            ))
            price = handle_no_such_element_exception(lambda: (
                price_element.find_element(By.CSS_SELECTOR, "[data-testid=\"price-and-discounted-price\"]").text.replace(",", "")
            ))

        # populate a new item with the scraped data
        item = {
            "url": url,
            "image": image,
            "title": title,
            "address": address,
            "distance": distance,
            "review_score": review_score,
            "review_count": review_count,
            "description": description,
            "original_price": original_price,
            "price": price
        }
        # add the new item to the list of scraped items
        items.append(item)


    output_file = f"Data/properties_{data_name}.csv"

    # Open the file and write data using csv.DictWriter
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["url", "image", "title", "address", "distance", "review_score", "review_count", "description", "original_price", "price"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header and rows
        writer.writeheader()
        writer.writerows(items)


    driver.quit()

    hotel_url_names = []

    for item in items:
        url = item['url']
        match = re.search(r'hotel/{}/(.+?)\.de\.html'.format(country_short), url)
        if match:
            hotel_url_name = match.group(1)
            hotel_url_names.append(hotel_url_name)


    df = pd.DataFrame(items)
    df["Hotel_key"] = hotel_url_names
    df['latitude'], df['longitude'] = zip(*df['address'].apply(find_location))

    df.to_json("Data/" + data_name + 'properties.json', orient='records', lines=True)
    print("Start scraping Hotel Website")

    # Change output dir
    with open('Scraping/config.yml', 'r') as file:
        config = yaml.safe_load(file)


    # Update the OUTPUT_DIR with the data_name
    config['OUTPUT_DIR'] = f"output/{data_name}"

    # Save the updated configuration back to the YAML file
    with open('Scraping/config.yml', 'w') as file:
        yaml.safe_dump(config, file)
        
    for hotel_url_name in tqdm(hotel_url_names, desc="Processing Hotels"):  
        result = subprocess.run(
            ["python", "run.py", hotel_url_name, country_short],
            cwd="Scraping",
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Return output as string
            check=True            # Raise an exception for non-zero exit codes
        )


def data_loader(data_name):
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  Hotel_Reviews = pd.read_csv("Data/" + data_name + ".csv")


  # Convert Review_Date to datetime and extract features
  Hotel_Reviews["date_object"] = pd.to_datetime(Hotel_Reviews["Review_Date"], format="%m%d%Y %H:%M:%S")
  #Hotel_Reviews["time"] = Hotel_Reviews["date_object"].astype(int) / 10**9  # Convert to Unix timestamp
  Hotel_Reviews["month"] = Hotel_Reviews["date_object"].dt.month
  Hotel_Reviews["num_date_object"] = Hotel_Reviews["date_object"].dt.day_of_year / 365  # Normalize by days in a year

  return Hotel_Reviews