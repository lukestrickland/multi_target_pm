library(dplyr)
library(stringr)
source("R/functions.R")

data_files <- list.files("data")
main_block_files <-  data_files[!grepl("practice|RM", data_files)]

#####Examine main experimental data

okdats <- stack_dats(main_block_files)
#Remove untested data
okdats <- okdats[okdats$RT != -1,]

#clean up df
okdats$S <- factor(okdats$S)
okdats$cond <- factor(okdats$cond)

table(okdats$S, okdats$cond, okdats$day)
hist(okdats$RT[okdats$RT < 3], breaks = 150, xlim = c(0, 2))

okdats %>%
  group_by(S, cond) %>%
  summarise(mean_acc = mean(C == R))

okdats %>%
  group_by(S, cond) %>%
  summarise(mean_RT = mean(RT))

###Practice ldt data
practice_files <-  data_files[grepl("practice", data_files)]
practicedats <- stack_dats(practice_files)

practicedats$S <- factor(practicedats$S)
practicedats$cond <- factor(practicedats$cond)

table(practicedats$S, practicedats$cond, practicedats$day)
hist(practicedats$RT[practicedats$RT < 3], breaks = 24, xlim = c(0, 1))

practicedats %>%
  group_by(S, cond) %>%
  summarise(mean_acc = mean(C == R))

practicedats %>%
  group_by(S, cond) %>%
  summarise(mean_RT = mean(RT))


#Examine RM test data
test_RM_files <-  data_files[grepl("test_RM", data_files)]
RMdats <- stack_dats(test_RM_files)

table(RMdats$C, RMdats$cond, RMdats$day)
hist(RMdats$RT[RMdats$RT < 3], breaks = 64,  xlim = c(0, 3))

okdats %>%
  group_by(cond, C) %>%
  summarise(mean_acc = mean(C == R))

okdats %>%
  group_by(S, cond) %>%
  summarise(mean_RT = mean(RT))

#Examine RM practice data
RM_files <-  data_files[grepl("RM", data_files)]
prac_RM_files <- RM_files[!grepl("test_RM", RM_files)]
prac_RMdats <- stack_dats(prac_RM_files)

table(prac_RMdats$C, prac_RMdats$cond, prac_RMdats$day)
hist(prac_RMdats$RT[prac_RMdats$RT < 3], breaks = 64,  xlim = c(0, 3))

okdats %>%
  group_by(cond, C) %>%
  summarise(mean_acc = mean(C == R))

okdats %>%
  group_by(S, cond) %>%
  summarise(mean_RT = mean(RT))
