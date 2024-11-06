# Hotel Review Project

This, or something similar, is what you see when you try to book a hotel on booking.com.
The most important information people use when booking a hotel is the room price, followed by the customer rating.

<img src="pics/Booking_page.png" width="60%">.

Reviews play such an important role in booking a hotel because the past experience of hotel guests is usually a pretty good approximation of the experience of potential future guests--including you.
Thus, people are willing to pay quite a bit more for hotels with good scores (see literature: https://api.semanticscholar.org/CorpusID:54877756 or https://api.semanticscholar.org/CorpusID:203160926).
On the other hand, this also means that people pay too much for hotels whose scores do not reflect their true quality. 

Here we want to better inform consumers by developing a Google Chrome extension that allows them to better judge how much the current rating is fair, too low or too high in three steps:

1. Trend Detector: which identifies hotels that have deteriorating review scores. The scores of these hotels are too high and should be used with caution.
2. Score Predictor: which predicts the near future review scores and therefore a fairer evaluation of the hotel.
3. Reason Extractor. An NLP model that identifies reviews that are associated with detrending hotels, thereby providing additional insights.

This could look like this:

<img src="pics/Hotel_example.png" width="60%">


   


_________________________________________________________________________________________________________
This project analyses Hotel Reviews and identifyies whether the scroing of a hotel is stable increasing or decreasing and provides review summaries.

# First explorative data
I first try to make a prototype with data from kaggle:
https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe 


# Scraping
/Scraping contains a python file 'run.py' which scrapes reviews from booking.com. Important  arguments it needs are hotel name as in the URL and the country code (e.g., us, de etc.).


```bash
python run.py 'paramount-new-york' 'us'
```
