
import pandas as pd
import re  # for regular expression matching


def data_loader():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  #Hotel_Reviews = pd.read_csv("../Data/Hotel_Reviews.csv")
  Hotel_Reviews = pd.read_csv("../Scraping/slim_data_11_12_2024.csv")


  # Read country data
  countries = pd.read_csv("../Data/countries.csv")

  # Add a "Country" column with NA values
  Hotel_Reviews["Country"] = pd.NA

  # Assign country based on pattern matching in Hotel_Address
  for country_name in countries["name"]:
    pattern = re.compile(country_name, re.IGNORECASE)  # Case-insensitive matching
    #Hotel_Reviews.loc[Hotel_Reviews["Hotel_Address"].str.contains(pattern), "Country"] = country_name

 
  # Convert Review_Date to datetime and extract features
  Hotel_Reviews["date_object"] = pd.to_datetime(Hotel_Reviews["Review_Date"], format="%m-%d-%Y %H:%M:%S")
  #Hotel_Reviews["time"] = Hotel_Reviews["date_object"].astype(int) / 10**9  # Convert to Unix timestamp
  Hotel_Reviews["month"] = Hotel_Reviews["date_object"].dt.month
  Hotel_Reviews["num_date_object"] = Hotel_Reviews["date_object"].dt.day_of_year / 365  # Normalize by days in a year

  return Hotel_Reviews
