

data_loader <- function(.){
  Hotel_Reviews <- readr::read_csv("../Data/Hotel_Reviews.csv", quote =",")
  
  
  countries <- readr::read_csv("../Data/countries.csv", quote ="\"")
  
  Hotel_Reviews$Country = NA
  for (i in countries$name){
    Hotel_Reviews$Country[str_detect(Hotel_Reviews$Hotel_Address, i)] = i
  }
  
  

  Hotel_Reviews <- Hotel_Reviews %>% mutate(time = as.numeric(as.POSIXct(Review_Date,format="%m/%d/%Y") ))
  date_object <- as.Date(Hotel_Reviews$Review_Date, format = "%m/%d/%Y")
  months <- month(date_object)
  Hotel_Reviews$date_object = date_object
  Hotel_Reviews$month = months
  Hotel_Reviews$num_date_object = as.numeric(date_object)/365
  
  return(Hotel_Reviews)
}

if(shiny_t==T){ 
# Define UI
ui <- fluidPage(
  mainPanel(
    selectInput("hotel", "Select Hotel:", choices = hotel_names),
    plotOutput("distPlot")
  )
)

# Define server logic
server <- function(input, output) {
  output$distPlot <- renderPlot({
    
    selected_hotel <- input$hotel
    
    # Filter data for the selected hotel
    filtered_data <- plot_data %>% filter(Hotel_Name == selected_hotel)
    
    
    # Check if the selected hotel has Neg == TRUE
    neg_hotel <- random_effct2 %>% filter(Name == selected_hotel & Neg == TRUE)
    
    
    # Plot
    p =  ggplot(filtered_data, aes(x = time_ref, y = Reviewer_Score2)) +
      geom_line(aes(y = Average_Score), color = "gray") +
      geom_point(aes(x = time_ref, y = Reviewer_Score2), alpha = 0.5) +
      geom_smooth(aes(x = time_ref, y = Reviewer_Score2), lty = "dashed") +
      geom_line(data= test_window  %>% filter(Hotel_Name == selected_hotel), aes(x=time_ref, y=Estimate)) +
      labs(title = "Predicted Reviewer Scores Over Time",
           x = "Date",
           y = "Predicted Reviewer Score") +
      coord_cartesian(ylim = c(6, 10)) + 
      theme_minimal() + 
      theme(legend.position = c(0.5, 0.9))
    if(random_effct2$Neg[random_effct2$Name == selected_hotel]==1)p =  p + geom_text(data = neg_hotel, aes(x = max(filtered_data$time_ref), y = 9, label = "!"), size = 10, color = "red", vjust = -1)
    if(random_effct2$Pos[random_effct2$Name == selected_hotel] ==1) p =  p + geom_text(data = neg_hotel, aes(x = max(filtered_data$time_ref), y = 9, label = "+"), size = 10, color = "green", vjust = -1)
    plot_grid(p,
              
              rbind(test_window  %>% filter(Hotel_Name == selected_hotel, time_ref > 0) %>% group_by(Hotel_Name) %>% summarise(pred = mean(Estimate), type="Prediction"),
                    test_data  %>% filter(Hotel_Name == selected_hotel, time_ref > 0) %>% group_by(Hotel_Name) %>% summarise(pred = mean(Reviewer_Score), type="Vacation average"),
                    Hotel_Reviews  %>% filter(Hotel_Name == selected_hotel, time_ref < 0) %>% group_by(Hotel_Name) %>% summarise(pred = mean(Reviewer_Score), type="Past average")) %>%
                ggplot(aes(x=type, y=pred)) + geom_bar(stat="identity") +      coord_cartesian(ylim = c(7, 10))  
    )
    
    
  })
}
}