
import pandas as pd
import re  # for regular expression matching


def data_loader():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  #Hotel_Reviews = pd.read_csv("../Data/Hotel_Reviews.csv")
  Hotel_Reviews = pd.read_csv("../Scraping/crete_11_12_2024.csv")




 
  # Convert Review_Date to datetime and extract features
  Hotel_Reviews["date_object"] = pd.to_datetime(Hotel_Reviews["Review_Date"], format="%m-%d-%Y %H:%M:%S")
  #Hotel_Reviews["time"] = Hotel_Reviews["date_object"].astype(int) / 10**9  # Convert to Unix timestamp
  Hotel_Reviews["month"] = Hotel_Reviews["date_object"].dt.month
  Hotel_Reviews["num_date_object"] = Hotel_Reviews["date_object"].dt.day_of_year / 365  # Normalize by days in a year

  return Hotel_Reviews
