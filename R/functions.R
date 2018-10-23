#Stack together the csvs for the experiment.
stack_dats <- function(files) {
  for (i in 1:length(files)) {
    single_df <-
      read.csv(paste("data/", files[i], sep = ""), stringsAsFactors =
                 FALSE)
    ppt <- str_match(files[i], "p._")[1]
    ppt <- substr(ppt, 1, str_length(ppt)-1)
    single_df$subj <- ppt
  
    if (i == 1) {
      full_data <- single_df
    } else {
      full_data <- rbind(full_data, single_df[colnames(full_data)])
    }
  }
  full_data
}