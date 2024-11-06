# Hotel Review project

This project analyses Hotel Reviews and identifyies whether the scroing of a hotel is stable increasing or decreasing and provides review summaries.


![Alt text](Booking_page.png)

_________________________________________________________________________________________________________

# First explorative data
I first try to make a prototype with data from kaggle:
https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe 


# Scraping
/Scraping contains a python file 'run.py' which scrapes reviews from booking.com. Important  arguments it needs are hotel name as in the URL and the country code (e.g., us, de etc.).


```bash
python run.py 'paramount-new-york' 'us'
```
