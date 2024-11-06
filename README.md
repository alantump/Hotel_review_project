# Hotel Review project

This, or something similar, is the what you see when trying to book a hotel on booking.com.
The most important inforaiton people use when booking a hotel is the room price followed by costumer rating.

<img src="pics/Booking_page.png" width="60%">

Scoring play such a vital role when booking a hotel because the past experiance of hotel guest is usually a pretty good approximation of the experiance of potential future guests---including yourself.
Thus, people are willing to pay quite a lot more for hotels with good scorings (see Literature: https://api.semanticscholar.org/CorpusID:54877756 or https://api.semanticscholar.org/CorpusID:203160926).
On the flipside this means that people I paying too much for hotels where the scoring are not reflecting their true quality. 

Here we want to better inform costumer by developing a google chrome extension which allows to better judge how much the current score is fair, too low or too high uisng three steps:

1. Trend detector: which identifies hotels which have detorating review scores. The scores of these hotels are too high and should be used with causion.
2. Score predictor: which predicts the near future review scores and therefore a fairer evaluation of the hotel.
3. Reason extractor. A NLP model which identifies reviews associated with detorating hotels, thereby providing additional insights.

This could look something like this:

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
