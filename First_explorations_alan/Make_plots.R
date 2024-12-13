source("functions.R")

Hotel_Reviews <- data_loader("keggle")

library(re)
gsub("[^0-9]", "", Hotel_Reviews$price[1])
prices <- sapply(Hotel_Reviews$price, function(x) gsub("[^0-9]", "", x))
print( )
plot(as.numeric(prices)~Hotel_Reviews$Reviewer_Score)
Hotel_Reviews$num_price = as.numeric(prices)

Hotel_Reviews %>% group_by(Hotel_Name)   %>% summarise(m=mean(num_price), m_score= mean(Reviewer_Score), n =n()) %>% filter(m<1000, n>100) %>% 
  ggplot(aes(x=m_score,y=m)) + geom_point() +geom_smooth()

tt = Hotel_Reviews %>% group_by(Hotel_Name) %>% summarise(m=mean(num_price), m_score= mean(Reviewer_Score), n =n())  %>% filter(m<1000, n>100)
lm(m ~ m_score, data=tt )

# Filter hotels with at least 500 reviews
Hotel_Reviews <- Hotel_Reviews %>%
  group_by(Hotel_Name) %>%
  filter(n() >= 200) %>% #, Country=="United Kingdom"
  ungroup()
min_number = 100


vec_pred=NULL
vec_weight=NULL
for(i in unique(Hotel_Reviews$Hotel_Name)){

  
  
  
  
  
  singel_Hotel_Reviews = Hotel_Reviews %>% filter(Hotel_Name==i)
  
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
      weight = exp(-days_since / (365 /3))  # Adjust the decay rate as needed
    )
  
  # Calculate the recency-weighted average
  recency_weighted_average <- with(singel_Hotel_Reviews, sum(Reviewer_Score * weight) / sum(weight))
  m_fit = lm(Reviewer_Score ~ date_object, data = singel_Hotel_Reviews)
  max_date <- max(singel_Hotel_Reviews$date_object, na.rm = TRUE)
  new_data <- data.frame(date_object = max_date)
  predicted_score <- predict(m_fit, newdata = new_data)
  mean_rating = round(mean(singel_Hotel_Reviews$Reviewer_Score),1)
  
  vec_pred = c(vec_pred,mean_rating-predicted_score)
  vec_weight = c(vec_weight,mean_rating-recency_weighted_average)
  
  
}
plot(vec_pred[abs(vec_weight)<1],vec_weight[abs(vec_weight)<1])
mean((vec_weight)<(-0.2))
mean((vec_weight)>(0.2))
mean(abs(vec_weight)>(0.2))

# Calculate the recency weights
singel_Hotel_Reviews %>%
  mutate(
    # Calculate the difference in days from the most recent date
    days_since = as.numeric(max(date_object) - date_object),
    # Calculate weights using an exponential decay function
    weight = exp(-days_since / (365/3))  # Adjust the decay rate as needed
  ) %>% ggplot(aes(y= weight, x=days_since )) + geom_point()









for(i in unique(Hotel_Reviews$Hotel_Name)){
  

singel_Hotel_Reviews = Hotel_Reviews %>% filter(Hotel_Name==i)

#singel_Hotel_Reviews = singel_Hotel_Reviews %>% mutate(New =ifelse(date_object>=(max(date_object) - 356),"New", "Old"))
num_hotels = nrow(singel_Hotel_Reviews)
mean_rating = round(mean(singel_Hotel_Reviews$Reviewer_Score),1)
max_y = max(singel_Hotel_Reviews %>% group_by(round(Reviewer_Score)) %>% summarise(n = n()) %>% select(n))
text_size = 6





# Calculate the recency weights
singel_Hotel_Reviews <- singel_Hotel_Reviews %>%
  mutate(
    # Calculate the difference in days from the most recent date
    days_since = as.numeric(max(date_object) - date_object),
    # Calculate weights using an exponential decay function
    weight = exp(-days_since / 365 *2)  # Adjust the decay rate as needed
  )

# Calculate the recency-weighted average
recency_weighted_average <- with(singel_Hotel_Reviews, sum(Reviewer_Score * weight) / sum(weight))

#m_fit = lm(Reviewer_Score ~ date_object, data = singel_Hotel_Reviews)
max_date <- max(singel_Hotel_Reviews$date_object, na.rm = TRUE)
new_data <- data.frame(date_object = max_date)
predicted_score <- recency_weighted_average#predict(m_fit, newdata = new_data)


overall_label_hight=1.35
change_label_hight=1.25

label_nudge = - 4

p = singel_Hotel_Reviews %>% ggplot(aes(Reviewer_Score)) +
  geom_histogram(binwidth = 1, color = "#CA9552", fill = alpha("#CA9552", 0.3)) +
  scale_x_continuous(breaks = seq(from = 1, to = 11, by = 1)) +
  geom_vline(xintercept = mean_rating, linetype = "longdash", size = 1, color = "#BC3751") +
  #annotate("text", label = paste("overall"), x = mean_rating, y = max_y * 1.1, size = text_size, color = "#BC3751", fontface = "italic") +
  
  
  # Add text annotations for the mean rating and total number of ratings
  annotate("text", label = paste("Average rating: ", mean_rating, sep = ""),
           x = mean_rating + label_nudge, y = max_y * overall_label_hight, size = text_size, hjust = 0, color = "#BC3751", fontface = "italic") +
  annotate("text", label = paste("Number of Ratings: ", num_hotels, sep = ""),
           x = 1, y = max_y * 1.0, size = text_size, hjust = 0.2, color = "Black", fontface = "italic") +
  
  # Customize the plot theme
  theme_classic() +
  theme(axis.ticks.y = element_blank(),
        axis.text.y = element_blank(),
        title = element_text(size = 25),
        axis.title = element_text(size = 18),
        axis.text = element_text(size = 14)) +
   labs(subtitle  = singel_Hotel_Reviews$Hotel_Name[1]) +# ggtitle() +
  xlab("Ratings") +
  ylab("Number of Ratings") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_y * 1.4))


if(abs(predicted_score-mean_rating)>0.2){
  
  # Add arrow from mean_rating to predicted_score
 p = p + geom_segment(aes(x = mean_rating, y = max_y * (change_label_hight-0.08), xend = predicted_score, yend = max_y * (change_label_hight-0.08)),
               arrow = arrow(length = unit(0.15, "inches")), color = "lightblue", size = 0.9)+
  annotate("text", label = paste("Recency weighted: ",round(predicted_score,1), sep = ""),
          x = mean_rating + label_nudge, y = max_y * change_label_hight, size = text_size, hjust = 0, color = "lightblue", fontface = "italic") +
   geom_segment(aes(x = predicted_score, xend = predicted_score, 
                    y = 0, yend = max_y * (change_label_hight - 0.08)),
                linetype = "longdash", size = 1, color = "lightblue")   
  
}

# Using gsub to remove spaces
no_spaces <- gsub("\\s+", "", i)

p = p +   stat_bin(binwidth = 1, geom = "text", aes(label = ..count..), vjust = -1, size = 6) 
ggsave(paste("Data/Histograms/",no_spaces,".png"),p, width =8, height = 4,dpi = 400)
}


