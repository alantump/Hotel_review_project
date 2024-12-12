source("functions.R")

Hotel_Reviews <- data_loader("keggle")


# Filter hotels with at least 500 reviews
Hotel_Reviews <- Hotel_Reviews %>%
  group_by(Hotel_Name) %>%
  filter(n() >= 200) %>% #, Country=="United Kingdom"
  ungroup()
min_number = 100


singel_Hotel_Reviews = Hotel_Reviews %>% filter(Hotel_Name==unique(Hotel_Reviews$Hotel_Name)[sample(90)[1]])

#singel_Hotel_Reviews = singel_Hotel_Reviews %>% mutate(New =ifelse(date_object>=(max(date_object) - 356),"New", "Old"))
num_hotels = nrow(singel_Hotel_Reviews)
mean_rating = round(mean(singel_Hotel_Reviews$Reviewer_Score),1)
max_y = max(singel_Hotel_Reviews %>% group_by(round(Reviewer_Score)) %>% summarise(n = n()) %>% select(n))
text_size = 6

m_fit = lm(Reviewer_Score ~ date_object, data = singel_Hotel_Reviews)
max_date <- max(singel_Hotel_Reviews$date_object, na.rm = TRUE)
new_data <- data.frame(date_object = max_date)
predicted_score <- predict(m_fit, newdata = new_data)


overall_label_hight=1.25
change_label_hight=1.35

label_nudge = - 3.6

p = singel_Hotel_Reviews %>% ggplot(aes(Reviewer_Score)) +
  geom_histogram(binwidth = 1, color = "#CA9552", fill = alpha("#CA9552", 0.3)) +
  scale_x_continuous(breaks = seq(from = 1, to = 11, by = 1)) +
  stat_bin(binwidth = 1, geom = "text", aes(label = ..count..), vjust = -1, size = 6) +
  geom_vline(xintercept = mean_rating, linetype = "longdash", size = 1, color = "#BC3751") +
  #annotate("text", label = paste("overall"), x = mean_rating, y = max_y * 1.1, size = text_size, color = "#BC3751", fontface = "italic") +
  
  
  # Add text annotations for the mean rating and total number of ratings
  annotate("text", label = paste("Average rating: ", mean_rating, sep = ""),
           x = mean_rating + label_nudge, y = max_y * overall_label_hight, size = text_size, hjust = 0, color = "#BC3751", fontface = "italic") +
  annotate("text", label = paste("Number of Ratings: ", num_hotels, sep = ""),
           x = 1, y = max_y * 1.35, size = text_size, hjust = 0.2, color = "#BC3751", fontface = "italic") +
  
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
 p = p + geom_segment(aes(x = mean_rating, y = max_y * change_label_hight, xend = predicted_score, yend = max_y * change_label_hight+0.1),
               arrow = arrow(length = unit(0.15, "inches")), color = "lightblue", size = 0.9)+
  annotate("text", label = paste("1 Year change ", sep = ""),
          x = mean_rating + label_nudge, y = max_y * change_label_hight, size = text_size, hjust = 0, color = "lightblue", fontface = "italic") 
  
}

p

