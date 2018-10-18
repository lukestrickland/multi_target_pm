library(dplyr)

data_files <- list.files("data")
main_block_files <-  data_files[!grepl("practice|RM", data_files)]

for (i in 1:length(main_block_files)) {
  single_df <-
    read.csv(paste("data/", main_block_files[i], sep = ""), stringsAsFactors =
               FALSE)
  if (i == 1) {
    full_data <- single_df
  } else {
    full_data <- rbind(full_data, single_df[colnames(full_data)])
  }
}

#Remove untested data
full_data <- full_data[full_data$RT!=-1,]
full_data$S <- factor(full_data$S)
full_data$acc <- full_data$C==full_data$R
hist(full_data$RT[full_data$RT < 3], breaks = 100, xlim = c(0, 3))

full_data %>%
  group_by(S,cond) %>%
  summarise(mean_acc= mean(acc))

full_data %>%
  group_by(S,cond) %>%
  summarise(mean_RT= mean(RT))

