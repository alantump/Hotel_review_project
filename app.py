import streamlit as st
import pandas as pd
#import plotly.express as px    
#from sklearn.ensemble import RandomForestRegressor
import pickle
import os
from dotenv import load_dotenv
from PIL import Image
import json
import numpy as np
import matplotlib.pyplot as plt


load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('OPENAI_API_KEY')
from functions.Rag_functions import process_question

import json

with open('hotel_classification_counts.json', 'r') as json_file:
    hotel_classification_counts = json.load(json_file)



# To retrieve a summary given a hotel name
def get_summary(hotel_name):
    with open('summarized_reviews_gr.json', 'r') as json_file:
        summaries = json.load(json_file)
    return summaries.get(hotel_name, "Summary not found.")

######
#Geofunctions
import pydeck as pdk

from geopy.geocoders import Nominatim

# Function to get geolocation data
def get_geolocation(description):
    geolocator = Nominatim(user_agent="geo_app")
    location = geolocator.geocode(description)
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










#####



def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*. The order is assumed
        to be from 'Strongly disagree' to 'Strongly aisagree'
    category_names : list of str
        The category labels.
    """
    
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    middle_index = data.shape[1]//2
    offsets = data[:, range(middle_index)].sum(axis=1) + data[:, middle_index]/2
    
    # Color Mapping
    category_colors = plt.get_cmap('coolwarm_r')(
        np.linspace(0.15, 0.85, data.shape[1]))
    
    fig, ax = plt.subplots(figsize=(4, 6))
    
    # Plot Bars
    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths - offsets
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)
    
    # Add Zero Reference Line
    ax.axvline(0, linestyle='--', color='black', alpha=.25)
    
    # X Axis
    ax.set_xlim(-90, 90)
    ax.set_xticks(np.arange(-100, 100, 25))
    ax.xaxis.set_major_formatter(lambda x, pos: str(abs(int(x))))
    
    # Y Axis
    ax.invert_yaxis()
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.xlabel('Percent of reviews mentioning this topic')

    # Ledgend
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    
    # Set Background Color
    fig.set_facecolor('#FFFFFF')

    return fig, ax

def data_loader_light():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  Hotel_Reviews = pd.read_csv("Scraping/crete_11_12_2024.csv")

  return Hotel_Reviews

# Load the lighter data
Hotel_Reviews = data_loader_light()

# Set the page configuration to use the whole width of the page
st.set_page_config(layout="wide")

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
    
    #hotels = Hotel_Reviews["Hotel_Name"].unique()

    # Count the number of reviews per hotel
    review_counts = Hotel_Reviews.groupby("Hotel_Name").size().reset_index(name="Review_Count")
    # Sort hotels by review count in descending order
    sorted_hotels = review_counts.sort_values(by="Review_Count", ascending=False)

    # Extract hotel names in sorted order
    hotels = sorted_hotels["Hotel_Name"].tolist()

    # Load the JSON file
    json_file = "Scraping/properties_gr.json"
    with open(json_file, "r") as file:
        hotel_data = [json.loads(line) for line in file]

    # Extract hotel titles
    hotel_titles = [hotel["title"] for hotel in hotel_data]

    # Layout for the select box and image display
    col1, col2 = st.columns([0.7, 0.3])

    # Select a hotel
    with col1:
        selected_hotel = st.selectbox(
            "Select a hotel to view from a dropdown or write hotel name partially to filter options:",
            hotels,
        )
        # Find the selected hotel's details safely
        selected_hotels = next(
            (hotel for hotel in hotel_data if hotel["title"] == selected_hotel), None
        )

        description=selected_hotels["address"]
        latitude, longitude = find_location(description)

        # Check if geolocation data is available
        if latitude is not None and longitude is not None:
          # Create a map centered around the location
          data = pd.DataFrame({
            'lat': [latitude],
            'lon': [longitude]
            })

          # Display the map
          # Define the initial view state
          view_state = pdk.ViewState(
              latitude=latitude,
              longitude=longitude,
              zoom=8.5,  # Set your desired zoom level here
              pitch=10
          )

          # Create a layer for the map
          layer = pdk.Layer(
              'ScatterplotLayer',
              data,
              get_position='[lon, lat]',
              get_radius=1200,
              get_color=[255, 0, 0],
              pickable=True
          )
          # Render the map with a lighter style
          st.pydeck_chart(pdk.Deck(
              layers=[layer],
              initial_view_state=view_state,
              map_style='mapbox://styles/mapbox/light-v9'  # Use a lighter map style
          ), height=400, width=600)
        else:
          print(f"Location not found for: {description}")


    # Display the selected hotel's details and image
    with col2:


        # Check if the hotel was found
        if selected_hotels:
            #st.image(selected_hotels["image"], caption=selected_hotels["title"], use_container_width =True)
            st.image(selected_hotels["image"], caption=selected_hotels["title"]) # deleting use_container_width =True because it was causing errors
            #st.write(f"**Address:** {selected_hotels.get('address', 'Not provided')}")
            #st.write(f"**Price:** {selected_hotels.get('price', 'Not provided')}")
            #st.write(f"**Description:** {selected_hotels.get('decription', 'Not provided')}")
        else:
            st.write("Image of the hotel not available.")

    if selected_hotel is not None:
      col1, col2, col3 = st.columns([0.3, 0.2,0.4])


      with col1:
          original_string = selected_hotel
          no_spaces = selected_hotel.replace(" ", "")
          image = Image.open("Data/Histograms/" + no_spaces + " .png")

          st.image(image, caption="Distribution of Reviews. If review got substancially worse or better the recency weighted average is shown.")
      
      with col2:
        category_names = ['positive', 'neutral', 'negative']
        counts = hotel_classification_counts[selected_hotel]
        print(counts)
        # Initialize a dictionary to store percentages per letter
        letter_percentages = {}

        # Collect all unique letters
        all_letters = set(counts['positive'].keys()).union(set(counts['negative'].keys()))

        # Calculate percentages for each letter
        for letter in all_letters:
            pos_count = counts['positive'].get(letter, 0)
            neg_count = counts['negative'].get(letter, 0)
            total_count = pos_count + neg_count
            
            pos_percentage = (pos_count / total_count) * 100 if total_count > 0 else 0
            neg_percentage = (neg_count / total_count) * 100 if total_count > 0 else 0
            
            letter_percentages[letter] = {
                'positive': pos_percentage,
                'negative': neg_percentage
            }
      
        results = {
        'Room and Service': [letter_percentages["A"]["positive"],0, letter_percentages["A"]["negative"]],
        "Food and Drinks": [letter_percentages["B"]["positive"],0, letter_percentages["B"]["negative"]],
        "Location": [letter_percentages["C"]["positive"],0, letter_percentages["C"]["negative"]],
        "Internet and Work": [letter_percentages["D"]["positive"],0, letter_percentages["D"]["negative"]],
        "Surprising or Unexpected": [letter_percentages["E"]["positive"],0, letter_percentages["E"]["negative"]]
        #"Other": [letter_percentages["F"]["positive"],0, letter_percentages["F"]["negative"]]
        }
        fig, ax = survey(results, category_names)

        st.pyplot(fig)
      with col3:
          st.markdown(get_summary(selected_hotel))


    filtered_data = Hotel_Reviews[
        (Hotel_Reviews["Hotel_Name"]==selected_hotel)
    ]


with tabs[1]:
  user_input = st.text_input("Please enter your hotel question:")

  result = process_question(user_input)
  # Display the output if the user has entered something
  if user_input:
      st.markdown(f"""**Answer:** {result}. 
                  
                  \n Are there other questions I can Help you with?""")
