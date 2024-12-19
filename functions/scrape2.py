import os
import pandas as pd
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the model and tokenizer
model_name = "Helsinki-NLP/opus-mt-mul-en"  # Multilingual to English
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Move the model to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def translate(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    outputs = model.generate(inputs["input_ids"], max_length=512, num_beams=4, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)




def load_dataframes(main_folder_path,data_name):
    dataframes = []
    for subdir, _, files in os.walk(main_folder_path):
        for file in files:
            if file == 'reviews_most_relevant.csv':
                file_path = os.path.join(subdir, file)
                df = pd.read_csv(file_path)
                pattern = rf'output/{data_name}/(.*?)_2024'
                match = re.search(pattern, subdir)
                if match and match.group(1):
                    df['Hotel_key'] = match.group(1)
                else:
                    print("No hotel found")
                dataframes.append(df)
    return dataframes

def concatenate_dataframes(dataframes):
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    concatenated_df = concatenated_df.drop_duplicates()
    return concatenated_df

def merge_with_properties(concatenated_df, properties_file):
    properties_df = pd.read_json(properties_file, orient='records', lines=True)
    full_data = pd.merge(concatenated_df, properties_df, on='Hotel_key', how='left')
    return full_data

def save_full_data(full_data, json_file, csv_file):
    full_data.to_json(json_file, orient='records', lines=True)
    full_data.to_csv(csv_file, index=False)

def prepare_slim_data(full_data):
    slim_data = full_data[["title", "review_post_date", "review_text_liked", "review_text_disliked", "rating", "user_country", "address", "price"]]
    slim_data = slim_data.rename(columns={
        'title': 'Hotel_Name',
        'review_post_date': 'Review_Date',
        'review_text_liked': 'Positive_Review',
        'review_text_disliked': 'Negative_Review',
        'rating': 'Reviewer_Score',
        "user_country": "Reviewer_Nationality"
    })
    return slim_data

def clean_for_csv(x):
    if isinstance(x, str):
        x = x.replace('\n', '').replace(',', '').replace('"', '').replace(';', '').replace('-', '').replace('_', '').replace('/', '')
    return x

def clean_slim_data(slim_data):
    return slim_data.applymap(clean_for_csv)

def translate_review(review):
    if pd.isna(review) or not review:
        return "NaN"
    try:
        lang = detect(review)
        if lang in ['de', 'fr', 'es']:
            return  translate(review, model, tokenizer)#GoogleTranslator(source=lang, target='en').translate(review)
        elif lang == 'en':
            return review
        else:
            return "NaN"
    except Exception as e:
        print(f"Error: {e}, Review: {review}")
        return "NaN"

def process_row(row):
    pos_review = row['Original_Positive_Review']
    neg_review = row['Original_Negative_Review']
    return translate_review(pos_review), translate_review(neg_review)

def translate_reviews(slim_data):
    slim_data['Original_Positive_Review'] = slim_data['Positive_Review']
    slim_data['Original_Negative_Review'] = slim_data['Negative_Review']
    
    print("Load translater:", detect("This is english"))
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_row, (row for _, row in slim_data.iterrows())), total=slim_data.shape[0], desc="Translating Reviews"))
    
    translated_reviews_pos, translated_reviews_neg = zip(*results)
    slim_data['Positive_Review'] = translated_reviews_pos
    slim_data['Negative_Review'] = translated_reviews_neg
    return slim_data

def process_reviews(data_name):
    main_folder_path = f"Scraping/output/{data_name}/"
    properties_file = f"Data/{data_name}properties.json"
    json_file = f"Data/{data_name}.json"
    csv_file = f"Data/{data_name}.csv"

    dataframes = load_dataframes(main_folder_path,data_name)
    concatenated_df = concatenate_dataframes(dataframes)
    print(concatenated_df)
    print(concatenated_df.isna().sum()) 

    rows, columns = concatenated_df.shape
    print(f"Number of rows: {rows}")
    print(f"Number of columns: {columns}")
    full_data = merge_with_properties(concatenated_df, properties_file)
    #save_full_data(full_data, json_file, csv_file)

    slim_data = prepare_slim_data(full_data)
    slim_data = clean_slim_data(slim_data)
    slim_data = translate_reviews(slim_data)
    save_full_data(slim_data, json_file, csv_file)
    #return slim_data

