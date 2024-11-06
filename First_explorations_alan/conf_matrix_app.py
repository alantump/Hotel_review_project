



# streamlit run conf_matrix_app.py



from sklearn.metrics import mean_squared_error, mean_absolute_error

import seaborn as sns

import matplotlib.pyplot as plt
import scipy.stats as stats
import streamlit as st

import statsmodels.api as sm
import numpy as np
import pandas as pd
import re  # for regular expression matching



def data_loader():
  """Loads data from CSV files, performs data cleaning and feature engineering.

  Returns:
    pandas.DataFrame: The processed hotel reviews dataset.
  """

  # Read hotel reviews data
  Hotel_Reviews = pd.read_csv("../Data/Hotel_Reviews.csv")

  # Read country data
  countries = pd.read_csv("../Data/countries.csv")

  # Add a "Country" column with NA values
  Hotel_Reviews["Country"] = pd.NA

  # Assign country based on pattern matching in Hotel_Address
  #for country_name in countries["name"]:
    #pattern = re.compile(country_name, re.IGNORECASE)  # Case-insensitive matching
    #Hotel_Reviews.loc[Hotel_Reviews["Hotel_Address"].str.contains(pattern), "Country"] = country_name

 
  # Convert Review_Date to datetime and extract features
  Hotel_Reviews["date_object"] = pd.to_datetime(Hotel_Reviews["Review_Date"], format="%m/%d/%Y")
  #Hotel_Reviews["time"] = Hotel_Reviews["date_object"].astype(int) / 10**9  # Convert to Unix timestamp
  Hotel_Reviews["month"] = Hotel_Reviews["date_object"].dt.month
  Hotel_Reviews["num_date_object"] = Hotel_Reviews["date_object"].dt.day_of_year / 365  # Normalize by days in a year

  return Hotel_Reviews

# Load the processed data
Hotel_Reviews = data_loader()





# Calculate trip time and start date
trip_time = 31 * 3
trip_start = Hotel_Reviews["date_object"].max() - pd.Timedelta(days=trip_time)
booking_time = trip_start
attention_window = 356 * 1.5

# Calculate time reference
Hotel_Reviews["time_ref"] = (Hotel_Reviews["date_object"] - booking_time).dt.days / 30.5

# Filter detection and test data
detection_data = Hotel_Reviews[(Hotel_Reviews["date_object"] < booking_time) &
                               (Hotel_Reviews["date_object"] > (booking_time - pd.Timedelta(days=attention_window)))]

test_data = Hotel_Reviews[(Hotel_Reviews["date_object"] > trip_start) &
                           (Hotel_Reviews["date_object"] < (trip_start + pd.Timedelta(days=trip_time)))]


model = sm.load('simple_lm.pickle')



# Streamlit App
st.title("Hotel Review Tendency Analysis")

# User Input for Sensetivity
sensitivity = st.slider("Select Significance Threshold (Sensetivity)", min_value=0.0, max_value=1.0, step=0.01, value=0.05)

# Calculate significance threshold based on user input
t_threshold = stats.t.ppf(1 - sensitivity / 2, df=model.df_resid)





# Create a DataFrame for interaction effects
time_effect_df = pd.DataFrame(model.params, columns=["Estimate"])
time_effect_df.index.name = "Name"
time_effect_df.reset_index(inplace=True)

# Extract hotel names and calculate t-statistics
time_effect_df["Hotel_Name"] = time_effect_df["Name"].str.extract(r"\[(.*?)\]")
time_effect_df["t_value"] = time_effect_df.index.map(lambda x: model.tvalues.iloc[x])
time_effect_df["Std.Error"] = time_effect_df.index.map(lambda x: model.bse.iloc[x])

time_effect_df = time_effect_df[model.params.index.str.contains(":")]


# Determine significance and direction
time_effect_df["Pos"] = (time_effect_df["t_value"] > t_threshold).astype(int)
time_effect_df["Neg"] = (time_effect_df["t_value"] < -t_threshold).astype(int)
time_effect_df["tendency"] = time_effect_df["Pos"] - time_effect_df["Neg"]







# In-sample predictions and error calculation
detection_data2 = detection_data.copy()  # Create a copy to avoid modifying original data
detection_data2['Estimate'] = model.predict(detection_data)


# Out-of-sample predictions and error calculation
test_data2 = test_data.copy()
test_data2['Estimate'] = model.predict(test_data)



# Calculate past average for each hotel
past_average = Hotel_Reviews[Hotel_Reviews['time_ref'] < 0].groupby('Hotel_Name')['Reviewer_Score'].mean().reset_index(name='past_average')

# Group test data by hotel and calculate mean review
grouped_test_data = test_data2.groupby('Hotel_Name')['Reviewer_Score'].mean().reset_index(name='mean_review')

# Join with time_effect_df and past_average
grouped_test_data = grouped_test_data.merge(time_effect_df, left_on='Hotel_Name', right_on='Hotel_Name')
grouped_test_data = grouped_test_data.merge(past_average, on='Hotel_Name')

# Calculate correct predictions
grouped_test_data['correct_neg'] = grouped_test_data['past_average'] > grouped_test_data['mean_review']
grouped_test_data['correct_pos'] = grouped_test_data['past_average'] < grouped_test_data['mean_review']

# Calculate proportions for negative and positive cases
proportion_data_neg = grouped_test_data.groupby(['Neg', 'correct_neg']).size().reset_index(name='m')
proportion_data_neg['proportion'] = proportion_data_neg['m'] / proportion_data_neg['m'].sum()

proportion_data_pos = grouped_test_data.groupby(['Pos', 'correct_pos']).size().reset_index(name='m')
proportion_data_pos['proportion'] = proportion_data_pos['m'] / proportion_data_pos['m'].sum()

# Calculate recall, precision, and F1-score for negative cases
true_positive_neg = proportion_data_neg[(proportion_data_neg['Neg'] == 1) & (proportion_data_neg['correct_neg'] == 1)]['m'].values[0]
false_negative_neg = proportion_data_neg[(proportion_data_neg['Neg'] == 0) & (proportion_data_neg['correct_neg'] == 1)]['m'].values[0]
false_positive_neg = proportion_data_neg[(proportion_data_neg['Neg'] == 1) & (proportion_data_neg['correct_neg'] == 0)]['m'].values[0]

recall_neg = true_positive_neg / (true_positive_neg + false_negative_neg)
precision_neg = true_positive_neg / (true_positive_neg + false_positive_neg)
f1_score_neg = 2 * (precision_neg * recall_neg) / (precision_neg + recall_neg)

# Calculate recall, precision, and F1-score for positive cases
true_positive_pos = proportion_data_pos[(proportion_data_pos['Pos'] == 1) & (proportion_data_pos['correct_pos'] == 1)]['m'].values[0]
false_negative_pos = proportion_data_pos[(proportion_data_pos['Pos'] == 0) & (proportion_data_pos['correct_pos'] == 1)]['m'].values[0]
false_positive_pos = proportion_data_pos[(proportion_data_pos['Pos'] == 1) & (proportion_data_pos['correct_pos'] == 0)]['m'].values[0]

recall_pos = true_positive_pos / (true_positive_pos + false_negative_pos)
precision_pos = true_positive_pos / (true_positive_pos + false_positive_pos)
f1_score_pos = 2 * (precision_pos * recall_pos) / (precision_pos + recall_pos)


# Display Results (assuming you have calculated relevant data)
st.subheader("Results:")
st.write("**Significance Threshold:**", t_threshold)


fig, axs = plt.subplots(1, 2, figsize=(12, 6))

sns.heatmap(proportion_data_neg.pivot_table(values='proportion', index='Neg', columns='correct_neg'), annot=True, fmt='.2f', cmap='coolwarm', ax=axs[0])
axs[0].set_title('Negative Cases')
axs[0].set_xlabel('Correct Negative')
axs[0].set_ylabel('Predicted Negative')
axs[0].text(0.5, 2.5, f'Recall: {recall_neg:.2f}\nPrecision: {precision_neg:.2f}\nF1-Score: {f1_score_neg:.2f}', ha='center', va='center')

sns.heatmap(proportion_data_pos.pivot_table(values='proportion', index='Pos', columns='correct_pos'), annot=True, fmt='.2f', cmap='coolwarm', ax=axs[1])
axs[1].set_title('Positive Cases')
axs[1].set_xlabel('Correct Positive')
axs[1].set_ylabel('Predicted Positive')
axs[1].text(0.5, 2.5, f'Recall: {recall_pos:.2f}\nPrecision: {precision_pos:.2f}\nF1-Score: {f1_score_pos:.2f}', ha='center', va='center')

plt.tight_layout()
st.pyplot(fig)

