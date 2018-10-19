library(dplyr)

data_files <- list.files("data")
main_block_files <-  data_files[!grepl("practice|RM", data_files)]

stack_csvs <- function(files) {
  for (i in 1:length(files)) {
    single_df <-
      read.csv(paste("data/", files[i], sep = ""), stringsAsFactors =
                 FALSE)
    if (i == 1) {
      full_data <- single_df
    } else {
      full_data <- rbind(full_data, single_df[colnames(full_data)])
    }
  }
  full_data
}

okdats <- stack_csvs(main_block_files)
#Remove untested data
okdats <- okdats[okdats$RT!=-1,]

#clean up df
okdats$S <- factor(okdats$S)
okdats$cond <- factor(okdats$cond)
okdats$acc <- okdats$C==okdats$R
hist(okdats$RT[okdats$RT < 3], breaks = 100, xlim = c(0, 3))

okdats %>%
  group_by(S,cond) %>%
  summarise(mean_acc= mean(acc))

okdats %>%
  group_by(S,cond) %>%
  summarise(mean_RT= mean(RT))

