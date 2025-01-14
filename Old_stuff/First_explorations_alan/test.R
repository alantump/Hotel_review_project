source("functions.R")


Hotel_Reviews <- read.csv("../Scraping/crete_11_12_2024.csv")


Hotel_Reviews <- Hotel_Reviews %>% mutate(time = as.numeric(as.POSIXct(Review_Date,format="%m-%d-%Y %H:%M:%S") ))
date_object <- as.Date(Hotel_Reviews$Review_Date, format = "%m-%d-%Y %H:%M:%S")
months <- month(date_object)
Hotel_Reviews$date_object = date_object
Hotel_Reviews$month = months
Hotel_Reviews$num_date_object = as.numeric(date_object)/365





##



library(prophet)
# Fit the model
m <- prophet(Hotel_Reviews %>% mutate(ds = date_object, y =Reviewer_Score) ,changepoint.prior.scale = 0.0005,
             yearly.seasonality=TRUE)

# Make future dataframe for predictions
#future <- make_future_dataframe(m, periods = trip_time) # Predict for the next 30 days

# Forecast
forecast <- predict(m, Hotel_Reviews %>% mutate(ds = date_object, y =Reviewer_Score)  )

Hotel_Reviews = Hotel_Reviews %>% mutate(cleaned_Review = Reviewer_Score + (forecast$weekly + forecast$yearly))

#prophet_plot_components(m, forecast)

###



recency_df = data.frame(recency= seq(0.0,2.5,0.2), error = NA, error0=NA,d_error=NA,d_error0=NA)
#recency_df = data.frame(recency= 0.01, error = NA, error0=NA,d_error=NA,d_error0=NA)

for(ii in 1:length(recency_df$recency)){
vec_pred=error_w= error_h0=error_w_s=NULL
vec_weight=NULL
for(i in unique(Hotel_Reviews$Hotel_Name)){
  
  
  
  
  
  #i=unique(Hotel_Reviews$Hotel_Name)[2]
  singel_Hotel_Reviews2 = Hotel_Reviews %>% filter(Hotel_Name==i) %>% mutate(New =ifelse(date_object>=(max(date_object) - (356/2)),"New", "Old"))
  singel_Hotel_Reviews_test = singel_Hotel_Reviews2 %>% filter(New=="New")
  singel_Hotel_Reviews = singel_Hotel_Reviews2 %>% filter(New=="Old")#
  length(unique(singel_Hotel_Reviews2$New))
  if(length(unique(singel_Hotel_Reviews2$New))==2){
  #singel_Hotel_Reviews = singel_Hotel_Reviews %>% mutate(New =ifelse(date_object>=(max(date_object) - 356),"New", "Old"))
  num_hotels = nrow(singel_Hotel_Reviews)
  mean_rating = round(mean(singel_Hotel_Reviews$Reviewer_Score),1)
  max_y = max(singel_Hotel_Reviews %>% group_by(round(Reviewer_Score)) %>% summarise(n = n()) %>% select(n))
  
  
  
  
  
  # Calculate the recency weights
  singel_Hotel_Reviews <- singel_Hotel_Reviews %>%
    mutate(
      # Calculate the difference in days from the most recent date
      days_since = as.numeric(max(date_object) - date_object),
      # Calculate weights using an exponential decay function
      weight = exp(-days_since / (365 /recency_df$recency[ii]))  # Adjust the decay rate as needed
    )
  
  # Calculate the recency-weighted average
  recency_weighted_average <- with(singel_Hotel_Reviews, sum(Reviewer_Score * weight) / sum(weight))
  #m_fit = lm(Reviewer_Score ~ date_object, data = singel_Hotel_Reviews)
  max_date <- max(singel_Hotel_Reviews$date_object, na.rm = TRUE)
  new_data <- data.frame(date_object = max_date)
  #predicted_score <- predict(m_fit, newdata = new_data)
  mean_rating = mean(singel_Hotel_Reviews$Reviewer_Score)
  mean_rating_future = mean(singel_Hotel_Reviews_test$Reviewer_Score)
  
   vec_pred = c(vec_pred,mean_rating-predicted_score)
   vec_weight = c(vec_weight,recency_weighted_average- mean_rating)
   error_h0 = c(error_h0,mean_rating_future-mean_rating)
   error_w = c(error_w,mean_rating_future-recency_weighted_average)
   error_w_s = c(error_w_s,abs(recency_weighted_average-mean_rating))
  
  
  }
}
plot(vec_weight,error_h0)
mean((vec_weight)<(-0.2))
mean((vec_weight)>(0.2))
mean(abs(vec_weight)>(0.2))

recency_df$error[ii]= mean(abs(error_w))#[error_w_s>0.2])
recency_df$error0[ii]= mean((vec_weight-error_h0)^2)#mean(abs(error_h0))#[error_w_s>0.2])
dummy=vec_weight-error_h0
recency_df$d_error[ii]= mean((dummy[abs(vec_weight)>0.2])^2)
recency_df$d_error0[ii]= mean(abs(error_h0)[abs(vec_weight)>0.2])





}


p3 =  recency_df %>% ggplot(aes(x=recency, y=(error0/error0[1])*3-2)) + geom_line(size=1.2) +  theme_minimal() + 
 ylab("Relavitve Error") + xlab("Decay Rate")
ggsave(paste("Data/decay_optim.png"),p3, width =2.5, height = 2.5,dpi = 400)

plot(recency_df$error0/recency_df$error0[1]~ recency_df$recency)

plot(recency_df$d_error~ recency_df$recency)
lines(recency_df$d_error/recency_df$d_error0~ recency_df$recency, col = "red", lwd = 2)  # lwd is the line width

abline(h=1)#recency_df$error0[1])

plot(recency_df$d_error/recency_df$d_error0~ recency_df$recency)

