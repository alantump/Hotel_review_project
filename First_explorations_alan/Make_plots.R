source("functions.R")

Hotel_Reviews <- data_loader("crete")

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





##



library(prophet)
# Fit the model
m <- prophet(Hotel_Reviews %>% mutate(ds = date_object, y =Reviewer_Score) ,changepoint.prior.scale = 0.0005,
             yearly.seasonality=TRUE)

# Make future dataframe for predictions
#future <- make_future_dataframe(m, periods = trip_time) # Predict for the next 30 days

# Forecast
forecast <- predict(m, Hotel_Reviews %>% mutate(ds = date_object, y =Reviewer_Score)  )

Hotel_Reviews = Hotel_Reviews %>% mutate(cleaned_Review = Reviewer_Score + forecast$weekly + forecast$yearly)

#prophet_plot_components(m, forecast)





#### Make example future plot

#5   8  10  11  24  27  51  61  66 105 107 145 146 165 170 177 178 181 185

i=unique(Hotel_Reviews$Hotel_Name)[178]
#dim(Hotel_Reviews %>% filter(Hotel_Name==i) )

singel_Hotel_Reviews2 = Hotel_Reviews %>% filter(Hotel_Name==i) %>% mutate(New =ifelse(date_object>=(max(date_object) - (356/2)),"Future", "Past"))

singel_Hotel_Reviews_f = singel_Hotel_Reviews2 %>% filter(New=="Future") %>% mutate(average=mean(Reviewer_Score))
singel_Hotel_Reviews_p = singel_Hotel_Reviews2 %>% filter(New=="Past") %>% mutate(average=mean(Reviewer_Score))#

# Calculate the recency weights
singel_Hotel_Reviews_p <- singel_Hotel_Reviews_p %>%
  mutate(
    # Calculate the difference in days from the most recent date
    days_since = as.numeric(max(date_object) - date_object),
    # Calculate weights using an exponential decay function
    weight = exp(-days_since / (365 /4))  # Adjust the decay rate as needed
  )
recency_weighted_average <- with(singel_Hotel_Reviews_p, sum(Reviewer_Score * weight) / sum(weight))
singel_Hotel_Reviews_p$recency_weighted_average = recency_weighted_average

p = ggplot(singel_Hotel_Reviews2, aes(x = date_object, y = Reviewer_Score, color = New)) +
  geom_point(alpha=0.2, size=0.8) +
  geom_line(data=singel_Hotel_Reviews_f, aes(y=average, x = date_object), color= "black", size=1) +
  geom_line(data=singel_Hotel_Reviews_p, aes(y=average, x = date_object), color = "#E69F00", size=1) +
  #geom_line(data=singel_Hotel_Reviews_p, aes(y=recency_weighted_average, x = date_object), color="#56B4E9", size=2) +
  #geom_smooth(method="lm") +
  labs(#title = "Reviewer Scores Over Time",
       x = "Date",
       y = "Reviewer Score") +
  coord_cartesian(ylim = c(6.5, 10)) + 
  theme_minimal() + 
  theme(legend.position = "top") +
  scale_color_manual(name = "",values = c("black", "#E69F00"),
                     labels = c("Future", "Past")) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size=2)))

p 
ggsave(paste("Data/hotel_average.png"),p, width =2.5, height = 2.5,dpi = 400)

####

# Calculate the recency weights
p2 = expand.grid(days_old = seq(0,(356*2),10), decay = c(0.5,1,2)) %>%
  mutate(
    weight = exp(-days_old / (365/decay))  # Adjust the decay rate as needed
  ) %>% ggplot(aes(y= weight, x=days_old, group=decay , color=factor(decay)) ) + geom_line(size=1.2) +   theme_minimal() +
  ylab("Weight") + xlab("Rating age [days]") +
  geom_vline(xintercept = 356, linetype ="dashed")+
  labs(color = "Decay Rate")   + theme(legend.position = c(0.8, 0.7))

p2
ggsave(paste("Data/decay.png"),p2, width =3, height = 3,dpi = 400)



##



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
      weight = exp(-days_since / (365 /2.5))  # Adjust the decay rate as needed
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


library(ggplot2)
library(dplyr)

test = data.frame(vec_weight, Name = unique(Hotel_Reviews$Hotel_Name), tendency = ifelse(abs(vec_weight) > 0.2, 1, 0)) %>%
  arrange(vec_weight)

test$Name <- factor(test$Name, levels = test$Name[order(test$vec_weight)])

pp = test %>% ggplot(aes(x = Name, y = vec_weight, colour = as.factor(tendency))) +  geom_hline(yintercept = seq(-1,1,0.2), linetype="dashed", color="gray") +
  coord_flip() +
  geom_hline(yintercept = 0) +    theme_classic() +#theme_cowplot() +#theme_minimal_vgrid() +
  geom_point() +
  theme(legend.position = "None",
        axis.text.y = element_blank(),  # Remove hotel names from y-axis
        axis.ticks.y = element_blank()) + # Remove ticks along with labels
  scale_color_manual(values = c("#F8766D", "#56B4E9", "#7CAE00")) +
  annotate("text", x = Inf, y = Inf, label = paste("Positive trend:", round(mean(test$vec_weight > 0.2), 2)), hjust = 1.01, vjust = 2 + 10, size = 4, color = "#56B4E9") +
  annotate("text", x = Inf, y = Inf, label = paste("No clear trend:", round(mean(test$tendency == 0), 2)), hjust = 1.01, vjust = 3.5 + 10, size = 4, color = "#F8766D") +
  annotate("text", x = Inf, y = Inf, label = paste("Negative trend:", round(mean(test$vec_weight < (-0.2)), 2)), hjust = 1.01, vjust = 5 + 10, size = 4, color = "#56B4E9") +
  xlab("Hotels of Crete") + ylab("Difference of \n simple and weighted average ratings") +
  scale_y_continuous(breaks = seq(-1, 1, by = 0.5), limits = c(-1,1)) 
pp
ggsave(paste("Data/tendencies.png"),pp, width =3.6, height = 3.6,dpi = 400)


# Calculate the recency weights
singel_Hotel_Reviews %>%
  mutate(
    # Calculate the difference in days from the most recent date
    days_since = as.numeric(max(date_object) - date_object),
    # Calculate weights using an exponential decay function
    weight = exp(-days_since / (365/2))  # Adjust the decay rate as needed
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
    weight = exp(-days_since / (365 /2.5))  # Adjust the decay rate as needed
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


