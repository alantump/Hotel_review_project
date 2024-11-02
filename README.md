# Hotel Review project


Project to analyse Hotel Reviews and identifying whether the scring of a hotel is stable increasing or decreasing.

# First explorative data
I first try to make a prototype with data from kaggle:
https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe 


# Scraping
/Scraping contains a python file 'run.py' which scrapes reviews from booking.com. Important  arguments it needs are hotel name as in the URL and the country code (e.g., us, de etc.).


```bash
python run.py 'paramount-new-york' 'us'
```