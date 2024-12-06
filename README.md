# Hotel Review Project

Booking.com is one of the largest online travel agencies and under the top 100 most visited websites of the world. Customers booked in more than a billion (10^9) nights on booking. Thus, improving aiding the booking and hotel choice procedure has the potential to improve a huge number of customers. 

This, or something similar, is what you see when you try to book a hotel on booking.com.
The most important information people use when booking a hotel is the room price, followed by the customer rating.

<img src="pics/Booking_page.png" width="60%">.

Reviews play such an important role in booking a hotel because the past experience of hotel guests is usually a pretty good approximation of the experience of potential future guests--including you.
Thus, people are willing to pay quite a bit more for hotels with good scores (see literature: https://api.semanticscholar.org/CorpusID:54877756 or https://api.semanticscholar.org/CorpusID:203160926).
On the other hand, this also means that people pay too much for hotels whose scores do not reflect their true quality.

Here we want to better inform consumers by developing a Google Chrome extension that allows them to better judge how much the current rating is fair, too low or too high in three steps:

1. Trend Detector: which identifies hotels that have deteriorating review scores. The scores of these hotels are too high and should be used with caution.
2. Score Predictor: which predicts the near future review scores and therefore a fairer evaluation of the hotel.
3. A Rag-system allowing the customer to ask questions about a specific hotel (e.g., How is the internet connection?) or generally Hotels in an area (Which hotels have good beds?).
4. Bonus: Reason Extractor. An NLP model that identifies reviews that are associated with deteriorating hotels, thereby providing additional insights.
5. Bonus: A Recommendation system allowing to find similar Hotels.


Why?

Nr. 4:
By training a machine learning model to predict a hotel's overall rating based on its reviews, we can pinpoint specific reviews that significantly impact this rating. Extracting this reviews allows the consumer to make more informed decisions when booking accommodations.

---

In the current phase consists of two main goals.

1. I first try to make a prototype with data from kaggle:
   https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe


2. Scraping
   /Scraping contains a python file 'run.py' which scrapes reviews from booking.com. Important arguments it needs are hotel name as in the URL and the country code (e.g., us, de etc.).

```bash
python run.py 'paramount-new-york' 'us'
```

## What has been done so far

We use a data set with reviews and scorings from end 2015 to end 2017 with 1492 hotels and 515.738 reviews.
This is how the average scroing look for a few example hotels:

![image](https://github.com/user-attachments/assets/83b9291d-b988-4f84-a4af-3acb4db63b62)

I split the data to a training set (before a reference day) and a training set (after a reference day).
I first build a trend detector by calculating a regression line for each hotel with data one year before the reference day.

```R
fit = lm(
   Reviewer_Score ~ 0 +  Hotel_Name + time_ref:Hotel_Name, data = train_data)
```

The regression line (time_ref:Hotel_Name) describe the change over time for each hotel.

Depending on how we set a threshold (the sensetivity of the detector), we that about 1/3 of the hotels are deteriorating.

![image](https://github.com/user-attachments/assets/e17d0272-81ff-4a06-853b-0a55dcb6287c)

Note that this trends describe a change per month.

Onnce we have a trend for each hotel, we can ask whether the hotel was indeed better or worse in the next 6 months.
For both, a deteration and improvement detector we can make a confusion matrix:

![image](https://github.com/user-attachments/assets/0c578479-b2b7-456d-9640-9811617e5214)

We want as many instances in the uper right or lower left corner.
Note that in this picture I set the sensetivity very low resulting in only a few false positives (i.e., in doubt say no trend).

Overall, this doesn't perform very well and should be improved further.

Once we have reasonable categorizations (deteroating, stable improving) we can train a model to identify reviews typically found in hotes of these classes:

| Hotel |                     Reviews (feature)                     | Class (target) |
| :---: | :-------------------------------------------------------: | :------------: |
|  "A"  |             "Breakfirst could start earlier"              |    "Stable"    |
|  "B"  | ""Disappointed!. We asked for up grade but not available" |  "Improving"   |
|  "C"  |         "There is a musty smell in the corridors"         | "Deteroating"  |

Once trained, this model should accurately identify relevant reviews for a hotel that is either deteriorating or improving.

Reviews have been summarized using Large Language Model and the output is showing possible reasons for deteriorating the score, e.g.:

Hotel X:

- Angry, post made available for public
- Room dirty, afraid to walk barefoot
- No staff to assist with luggage

Hotel Y:

- No trolley or staff for luggage assistance
- Hotel looks like 3-star, not 4
- AC was useless during hot week
- Free Wi-Fi didn't work on 3rd floor





# Keys



Create a file named `.env` in the root directory of this project and save your openai key there:

```plaintext
# .env
OPENAI_API_KEY=your_openai_api_key_here
```
The `.gitignore` file has `.env` included, thus it should be save.






