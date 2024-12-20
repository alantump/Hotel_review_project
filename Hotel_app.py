import streamlit as st
import pandas as pd
#import plotly.express as px    
#from sklearn.ensemble import RandomForestRegressor
import os
from dotenv import load_dotenv
from PIL import Image
import json
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk


from functions.scrape1 import data_loader, find_location
from functions.Rag_functions import process_question, get_retriever_faiss


load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('OPENAI_API_KEY')




def list_folders_in_directory(directory_path):
    try:
        # List all entries in the directory
        entries = os.listdir(directory_path)
        
        # Filter out entries that are directories
        folders = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
        
        return folders
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage



# To retrieve a summary given a hotel name
def get_summary(hotel_name):
    with open(f'Data/summarized_reviews_{data_name}.json', 'r') as json_file:
        summaries = json.load(json_file)
    return summaries.get(hotel_name, "Summary not found.")












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


# Load the lighter data

# Set the page configuration to use the whole width of the page
st.set_page_config(layout="wide")

# Write the headline as a header
st.title("Hotel Reviews Analyzer")
# Write the subtitle
# st.write(
#     "Booking.com is one of the largest online travel agencies and one of the top 100 most visited websites in the world."
#      " As such, improving the booking and hotel selection process has the potential to improve the experience for a large"
#       " number of customers. While reviews play an important role in the booking process, extracting the required"
#        " information from the reviews provided is often cumbersome. In this project, we want to develop an application"
#         " that analyses hotel reviews and provides valuable information that allows customers to make more informed"
#          " decisions based on the past experiences of others."
# )

directory_path = './Data/faiss_index'
folders = list_folders_in_directory(directory_path)

data_name = st.selectbox(
    "Select the data source:",
    folders,
)
Hotel_Reviews = data_loader(data_name)


index_path = f"./Data/faiss_index/{data_name}"
retriever = get_retriever_faiss(index_path, local=True) #change to openAI by adding local= False

with open(f'Data/hotel_classification_counts_{data_name}.json', 'r') as json_file:
    hotel_classification_counts = json.load(json_file)



st.subheader("Personal Review Analyzer Assistant")
col1, col2, = st.columns([0.75,0.25])

# Initialize session state for user input
if 'previous_input' not in st.session_state:
    st.session_state['previous_input'] = ''


with col1:
    user_input = st.text_input("Please enter your hotel question:")

    # Check if the input has changed
    if user_input != st.session_state['previous_input']:
        # Update the session state
        st.session_state['previous_input'] = user_input

        # Process the question and display the result
        if user_input:
            result = process_question(user_input, retriever)
            st.markdown(f"""**Answer:**\n {result} 
                        
            \n Are there other questions I can Help you with?""")
      
                  
          

st.subheader("Hotel Overview")

#hotels = Hotel_Reviews["Hotel_Name"].unique()

# Count the number of reviews per hotel
review_counts = Hotel_Reviews.groupby("Hotel_Name").size().reset_index(name="Review_Count")
# Sort hotels by review count in descending order
sorted_hotels = review_counts.sort_values(by="Review_Count", ascending=False)

# Extract hotel names in sorted order
hotels = sorted_hotels["Hotel_Name"].tolist()

# Load the JSON file
json_file = f"./Data/{data_name}properties.json"
with open(json_file, "r") as file:
    hotel_data = [json.loads(line) for line in file]

# Extract hotel titles
hotel_titles = [hotel["title"] for hotel in hotel_data]




col1, col2, = st.columns([0.5,0.5])

with col1:
    selected_hotel = st.selectbox(
        "Select a hotel to view from a dropdown or write hotel name partially to filter options:",
        hotels,
    )
    # Find the selected hotel's details safely
    selected_hotels = next(
        (hotel for hotel in hotel_data if hotel["title"] == selected_hotel), None
    )




# Layout for the select box and image display
col1, col2, col3, col4 = st.columns([0.27, 0.2,0.35,0.18])

# Select a hotel
with col1:


    if selected_hotels:
        description=selected_hotels["address"]
        print(description)
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
              zoom=7.9,  # Set your desired zoom level here
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
          ), height=250, width=400)
        else:
          print(f"Location not found for: {description}")
    else:
        st.write("Hotel address not available.")

    


# Display the selected hotel's details and image
with col2:


    # Check if the hotel was found
    if selected_hotels:
        #st.image(selected_hotels["image"], caption=selected_hotels["title"], use_container_width =True)
        #st.image(selected_hotels["image"], caption=selected_hotels["title"]) # deleting use_container_width =True because it was causing errors
        st.image(selected_hotels["image"], caption=selected_hotels["title"], width=250) # (use_column_width) change to use_container_width on alans pc
        #st.write(f"**Address:** {selected_hotels.get('address', 'Not provided')}")
        #st.write(f"**Price:** {selected_hotels.get('price', 'Not provided')}")
        #st.write(f"**Description:** {selected_hotels.get('decription', 'Not provided')}")
    else:
        st.write("Image of the hotel not available.")
with col3:
      original_string = selected_hotel
      no_spaces = selected_hotel.replace(" ", "")
      image = Image.open(f"./Data/Histograms/{data_name}/" + no_spaces + ".png")

      st.image(image, caption="Distribution of Reviews. ") #If review got substancially worse or better the recency weighted average is shown.

if selected_hotel is not None:
  col1, col2, col3 = st.columns([ 0.3,0.5,0.2])


      
  
  with col1:
    category_names = ['positive', 'neutral', 'negative']
    counts = hotel_classification_counts[selected_hotel]
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
  with col2:
      st.markdown(get_summary(selected_hotel))


filtered_data = Hotel_Reviews[
    (Hotel_Reviews["Hotel_Name"]==selected_hotel)
]
