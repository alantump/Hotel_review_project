import streamlit as st
import pandas as pd
#import plotly.express as px    
#from sklearn.ensemble import RandomForestRegressor
import pickle
import os
#from model import train_and_save_model

# file_path = 'global_development_data.csv'

# # Load the CSV file
# data = pd.read_csv(file_path)
# min_year = int(data['year'].min())
# max_year = int(data['year'].max())

import re
def data_loader():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  Hotel_Reviews = pd.read_csv("Data/Hotel_Reviews.csv")

  # Read country data
  countries = pd.read_csv("Data/countries.csv")

  # Add a "Country" column with NA values
  Hotel_Reviews["Country"] = pd.NA

  # Assign country based on pattern matching in Hotel_Address
  for country_name in countries["name"]:
    pattern = re.compile(country_name, re.IGNORECASE)  # Case-insensitive matching
    Hotel_Reviews.loc[Hotel_Reviews["Hotel_Address"].str.contains(pattern), "Country"] = country_name

 
  # Convert Review_Date to datetime and extract features
  Hotel_Reviews["date_object"] = pd.to_datetime(Hotel_Reviews["Review_Date"], format="%m/%d/%Y")
  #Hotel_Reviews["time"] = Hotel_Reviews["date_object"].astype(int) / 10**9  # Convert to Unix timestamp
  Hotel_Reviews["month"] = Hotel_Reviews["date_object"].dt.month
  Hotel_Reviews["num_date_object"] = Hotel_Reviews["date_object"].dt.day_of_year / 365  # Normalize by days in a year

  return Hotel_Reviews

# Load the processed data
#Hotel_Reviews = data_loader()

def data_loader_light():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  Hotel_Reviews = pd.read_csv("Data/Hotel_Reviews.csv")

  return Hotel_Reviews

# Load the lighter data
Hotel_Reviews = data_loader_light()

# Set the page configuration to use the whole width of the page
st.set_page_config(layout="wide")
#### Model
# Check if the model pickle file exists
# if not os.path.exists('life_expectancy_model.pkl'):
#     train_and_save_model()
# # Load the trained model
# with open('life_expectancy_model.pkl', 'rb') as file:
#     model = pickle.load(file)

####
st.write("Content for Reviews Analyzer")


# Write the headline as a header
st.title("Hotel Reviews Analyzer")

# Write the subtitle
st.write(
    "Booking.com is one of the largest online travel agencies and one of the top 100 most visited websites in the world."
     " As such, improving the booking and hotel selection process has the potential to improve the experience for a large"
      " number of customers. While reviews play an important role in the booking process, extracting the required"
       " information from the reviews provided is often cumbersome. In this project, we want to develop an application"
        " that analyses hotel reviews and provides valuable information that allows customers to make more informed"
         " decisions based on the past experiences of others."
)

# Create 3 tabs
tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

# # Content for each tab
with tabs[0]:
    hotels = Hotel_Reviews["Hotel_Name"].unique()
    selected_hotel = st.multiselect("Select a hotel to view from a dropdown or write hotel name partially to filter options:", 
                                    hotels, 
                                    #default="Hotel Arena", 
                                    max_selections = 1)

    # selected_hotels = st.selectbox(
    # "How would you like to be contacted?",
    # ("Email", "Home phone", "Mobile phone"),)
    
    # st.write("You selected:", option)

    
    #selected_year_range = st.slider("Select the year range", min_year, max_year, (min_year, max_year))


    filtered_data = Hotel_Reviews[
        (Hotel_Reviews["Hotel_Name"].isin(selected_hotel))
    ]
    st.write("Explore the dataset:")
    st.dataframe(filtered_data)

    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name='filtered_data.csv',
    )

# with tabs[1]:
#     st.write("Content for Country Deep Dive")

# with tabs[2]:
   
#     countries = data['country'].unique()
#     selected_countries = st.multiselect("Select countries to view", countries, default="Germany")

    
#     selected_year_range = st.slider("Select the year range", min_year, max_year, (min_year, max_year))


#     filtered_data = data[
#         (data['country'].isin(selected_countries)) & 
#         (data['year'] >= selected_year_range[0]) & 
#         (data['year'] <= selected_year_range[1])
#     ]
#     st.write("Explore the dataset:")
#     st.dataframe(filtered_data)

#     csv = filtered_data.to_csv(index=False)
#     st.download_button(
#         label="Download filtered data as CSV",
#         data=csv,
#         file_name='filtered_data.csv',
#     )