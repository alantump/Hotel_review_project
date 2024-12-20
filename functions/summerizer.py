import os
import pandas as pd
import re
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import json
from tqdm import tqdm
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain import LLMChain

import torch


# Assuming necessary imports for LLM and other components are already done

class TextSummarizer:
    # Initialization and other methods as defined previously
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(torch.cuda.is_available())  # Should return True if GPU is available

    def __init__(self):
        #self.apikey = self.fetch_api_key()
        self.llm = OllamaLLM(model="llama3.2", max_tokens=4000)

    # Define other methods like average_sentences, summarize_text, etc.

    def topic_classification_local(self, input_text):
        # Define the system template for categorizing reviews
        prompt_template = """You are a fair but critical assistant that categorizes reviews.
                        The reviews can be categorized into 6 categories: Room and Service, Food and Drinks, Location, Internet and Work, Surprising or Unexpected, or Other. Here are some keywords for each topic:
                        (A) "Room and Service": ["room", "clean", "tidy", "smell", "large", "bathroom", "bed", "beds", "TV", "bar", "conditioner", "shower", "Service", "friendly"] - all aspects of describing the status of the room and the quality of the service,
                        (B) "Food and Drinks": ["drinks", "cocktails", "bottle", "breakfast", "dinner", "menu", "caffee", "tee", "delicious", "continental", "waiter", "restaurant"] - all aspects describing the quality of food like breakfast and bar,
                        (C) "Location": ["close", "far", "next", "park", "train", "bicicle", "car", "walk", "tee", "building", "neighborhood", "cab service", "airport", "subway", "stairs"] - all aspects describing the location, surrounding, and connection of the hotel,
                        (D) "Internet and Work": ["wifi", "Internet", "connection", "work", "password", "computer", "meeting", "signal"] - all aspects describing the ability to work from the hotel with a focus on internet connection,
                        (E) "Surprising or Unexpected": ["everything", "honestly", "surprising", "change", "unfortunately", "refund"] - all aspects which are surprisingly and not expected by the reviewer,
                        (F) "Other" - everything else

                        Please provide an answer in this format whereby X is the category from A to F:

                        Categories: ([X, X])

                        So if someone mentions food and Internet you only answer with:

                        Categories: ([B, D])

                        Here is the review:
                        "{text}"
                        """
        
        prompt = PromptTemplate.from_template(prompt_template)
        chain_fusion = LLMChain(llm=self.llm, prompt=prompt)
        return chain_fusion.run(input_text)
    

    def summarize_text_local(self, input_text):
        prompt_template_sum = """You are an fair but critical assistant that is able to read a piece of text and summarize it. Please provide a one sentence general summary.
                    Additionally you will write a summary sentence on each of the for topics: Room, Food and Drinks, Location, Internet and Work and Surprise.
                    Here are some keywords for each topic 
                "Room and Service": ["room", "clean", "tidy", "smell", "large","bathroom", "bed", "beds", "TV", "bar", "conditioner","shower", "Service","friendly"] all aspects of describing the status of the room and the quality of the service,
                "Food and Drinks": ["drinks", "cocktails", "bottle", "breakfast", "dinner", "menu", "caffee", "tee", "delicious", "continental", "waiter","restaurant "] all aspects describing the quality of food like breakfast and bar,
                "Location": ["close", "far", "next", "park", "train", "bicicle", "car", "walk", "tee", "building", "neighborhood", "cab service", "airport", "subway", "stairs"] all aspects describing the location, surrounding and connection of the hotel,
                "Internet and Work": ["wifi", "Internet", "connection", "work", "password", "computer", "meeting", "signal"] all aspects describing abilty to work from the hotel with a focus on internet connection,
                "Surprising or Unexpected": ["everything", "honestly", "surprising", "change", "unfortunately", "refund"] all aspects which are supringly and not expected by the reviewer,
                Feel free to say that the reviews do not specifically address certain topics.

                Here is the review:
                "{text}"
                """
        prompt = PromptTemplate.from_template(prompt_template_sum)
        chain_fusion = LLMChain(llm=self.llm, prompt=prompt)
        return chain_fusion.run(input_text)



def classify_review(review, summarizer):
    if pd.isna(review) or not review:
        return "NaN"
    try:
        input_string = summarizer.topic_classification_local(review)
        matches = re.findall(r'\[([A-Z, ]+)\]', input_string)
        if matches:
            elements = [element.strip() for element in matches[0].split(',')]
        return elements
    except:
        print("AI error")
        time.sleep(2)
        return "NaN"

def process_row(row, summarizer):
    pos_review = row['Positive_Review']
    neg_review = row['Negative_Review']
    return classify_review(pos_review, summarizer), classify_review(neg_review, summarizer)

def classify_reviews(used_data, summarizer):
    classified_reviews_pos = []
    classified_reviews_neg = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(tqdm(executor.map(lambda row: process_row(row, summarizer), (row for _, row in used_data.iterrows())), total=used_data.shape[0], desc="Classifying Reviews"))

    classified_reviews_pos, classified_reviews_neg = zip(*results)
    return classified_reviews_pos, classified_reviews_neg

def count_classifications(classified_reviews):
    flattened_list = [item for sublist in classified_reviews if isinstance(sublist, list) for item in sublist]
    return Counter(flattened_list)

def categorize_reviews(used_data,data_name):
    summarizer = TextSummarizer()
    classified_reviews_pos, classified_reviews_neg = classify_reviews(used_data, summarizer)
    used_data['classified_reviews_pos'] = classified_reviews_pos
    used_data['classified_reviews_neg'] = classified_reviews_neg

    hotel_classification_counts = {}
    grouped_pos = used_data.groupby('Hotel_Name')['classified_reviews_pos']
    grouped_neg = used_data.groupby('Hotel_Name')['classified_reviews_neg']

    for hotel_name, reviews in grouped_pos:
        letter_counts = count_classifications(reviews)
        if hotel_name not in hotel_classification_counts:
            hotel_classification_counts[hotel_name] = {}
        hotel_classification_counts[hotel_name]['positive'] = dict(letter_counts)

    for hotel_name, reviews in grouped_neg:
        letter_counts = count_classifications(reviews)
        if hotel_name not in hotel_classification_counts:
            hotel_classification_counts[hotel_name] = {}
        hotel_classification_counts[hotel_name]['negative'] = dict(letter_counts)

    with open(f'Data/hotel_classification_counts_{data_name}.json', 'w') as json_file:
        json.dump(hotel_classification_counts, json_file, indent=4)

def summarize_reviews(used_data, data_name):

    used_data['MergedColumn'] = (
        '' +'Hotel: ' + used_data['Hotel_Name'] + 
        '. Positive Guest Review: ' + used_data['Positive_Review'] + 
        '. ' +'Hotel: ' + used_data['Hotel_Name'] + 
        '. Negative Guest Review: '+ used_data['Negative_Review'] + "\n"
    )

    used_data2 = used_data.dropna(subset=['MergedColumn'])
    grouped_reviews = used_data2.groupby('Hotel_Name')['MergedColumn'].apply(lambda x: ' '.join(x)).to_dict()
    # Initialize your summarizer
    summarizer = TextSummarizer()

    # Summarize each hotel's reviews
    summarized_reviews = {}
    for hotel, reviews in grouped_reviews.items():
        summarized_reviews[hotel] = summarizer.summarize_text_local(reviews)

    # Store summarized reviews in a JSON file
    with open(f'Data/summarized_reviews_{data_name}.json', 'w') as json_file:
        json.dump(summarized_reviews, json_file, indent=4)
