import streamlit as st
import pandas as pd
#import plotly.express as px    
#from sklearn.ensemble import RandomForestRegressor
import pickle
import os
from dotenv import load_dotenv
from PIL import Image
import json

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('OPENAI_API_KEY')
from functions.Rag_functions import process_question


# To retrieve a summary given a hotel name
def get_summary(hotel_name):
    with open('summarized_reviews_gr.json', 'r') as json_file:
        summaries = json.load(json_file)
    return summaries.get(hotel_name, "Summary not found.")


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
    #selected_hotel2 = st.multiselect("Select a hotel to view from a dropdown or write hotel name partially to filter options:", 
    #                                hotels, 
    #                                #default="Hotel Arena", 
    #                                max_selections = 1)
    selected_hotel = st.selectbox("Select a hotel to view from a dropdown or write hotel name partially to filter options:", 
                                hotels, index=None)

    # selected_hotels = st.selectbox(
    # "How would you like to be contacted?",
    # ("Email", "Home phone", "Mobile phone"),)
    
    # st.write("You selected:", option)

    
    #selected_year_range = st.slider("Select the year range", min_year, max_year, (min_year, max_year))
    if selected_hotel is not None:
      col1, col2 = st.columns(2)


      with col1:
          original_string = selected_hotel
          no_spaces = selected_hotel.replace(" ", "")
          image = Image.open("Data/Histograms/" + no_spaces + " .png")

          st.image(image, caption="Distribution of Reviews. If review got substancially worse or better the recency weighted average is shown.")
      with col2:
          st.markdown(get_summary(selected_hotel))


    filtered_data = Hotel_Reviews[
        (Hotel_Reviews["Hotel_Name"]==selected_hotel)
    ]
    st.write("Explore the dataset:")
    st.dataframe(filtered_data)

    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name='filtered_data.csv',
    )














with tabs[1]:
  user_input = st.text_input("Please enter your hotel question:")

  result = process_question(user_input)
  # Display the output if the user has entered something
  if user_input:
      st.markdown(f"""**Answer:** {result}. 
                  
                  \n Are there other questions I can Help you with?""")



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