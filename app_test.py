import streamlit as st
import pandas as pd
#import plotly.express as px    
#from sklearn.ensemble import RandomForestRegressor
import pickle
import os
import openai

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('OPENAI_API_KEY')


from functions.Rag_functions import process_question



#from model import train_and_save_model

# file_path = 'global_development_data.csv'

# # Load the CSV file
# data = pd.read_csv(file_path)
# min_year = int(data['year'].min())
# max_year = int(data['year'].max())


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
tabs = st.tabs(["Global Overview", "Country Deep Dive", "Data Explorer"])
with tabs[0]:

    user_input = st.text_input("Please enter your hotel question:")

    result = process_question(user_input)
    # Display the output if the user has entered something
    if user_input:
        st.markdown(f"""**Answer:** {result}. 
                    
                    \n Are there other questions I can Help you with?""")



# # Content for each tab
# with tabs[0]:
#     st.header("Global Overview - Key Statistics")
#     year = st.slider("Select Year for Visualisation", 1990, 2016)
#     filtered_data = data[data["year"] == year]
#     col1, col2, col3, col4 = st.columns(4)
#     col1.write("Mean of life expectancy")
#     mean_life_expectancy = filtered_data["Life Expectancy (IHME)"].mean()
#     col1.subheader(f'{mean_life_expectancy:.2f}')
#     col2.write("Global median of GDP per capita")
#     medianGDP = filtered_data["GDP per capita"].median()
#     col2.subheader(f'${medianGDP:,.0f}')
#     col3.write("Global Poverty Average")
#     headcount_ratio_upper_mid_income_povline_mean = filtered_data["headcount_ratio_upper_mid_income_povline"].mean()
#     col3.subheader(f'{headcount_ratio_upper_mid_income_povline_mean:.0f}%')
#     col4.write("Number of countries")
#     num_countries = len(filtered_data["country"].unique())
#     col4.subheader(f"{num_countries:.0f}")
#     fig = px.scatter(filtered_data,
#                      x="GDP per capita",
#                      y="Life Expectancy (IHME)",
#                      hover_name='country',
#                      log_x=True,
#                      size='Population',
#                      color='country',
#                      title=f'Life Expectancy vs GDP per capita ({year})',
#                      labels={
#                          'GDP per capita': 'GDP per Capita (USD)',
#                          'Life Expectancy (IHME)': 'Life Expectancy (Years)'
#                      })
#     st.plotly_chart(fig)

#     # Model stuff again


#     st.write("Predict Life Expectancy:")
#     input_gdp = st.number_input("Enter GDP per capita", min_value=0.0, value=medianGDP)
#     input_poverty = st.number_input("Enter headcount ratio upper mid income povline", min_value=0.0, value=headcount_ratio_upper_mid_income_povline_mean)
#     input_year = st.number_input("Enter Year for prediction", min_value=min_year, max_value=max_year, value=2000)
#     input_data = pd.DataFrame({
#             'GDP per capita': [input_gdp],
#             'headcount_ratio_upper_mid_income_povline': [input_poverty],
#             'year': [input_year]
#     })    
    
#     # execute the prediction by clicking on predict button
#     if st.button("Predict"):
#         prediction = model.predict(input_data)
#         st.write(f"Estimated Life Expectancy: {prediction[0]:.2f} years")
    
#     features = ['GDP per capita', 'headcount_ratio_upper_mid_income_povline', 'year']
#     feature_importances = model.feature_importances_
#     importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importances})
#     importance_df = importance_df.sort_values(by='Importance', ascending=False)
    
#     fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h', title='Feature Importance')
#     st.plotly_chart(fig)

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