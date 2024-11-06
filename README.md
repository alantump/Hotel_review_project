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
In the current phase consists of two main goals.

1. I first try to make a prototype with data from kaggle:
https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe 


2. Scraping
/Scraping contains a python file 'run.py' which scrapes reviews from booking.com. Important  arguments it needs are hotel name as in the URL and the country code (e.g., us, de etc.).

```bash
python run.py 'paramount-new-york' 'us'
```

## What Alan has done so far

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



