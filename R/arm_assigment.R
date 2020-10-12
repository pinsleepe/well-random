#!/usr/bin/env Rscript
# library(renv)
library(Minirand)
library(dotenv)
library(DBI)
library(argparser)

# renv::init()
# renv::restore()

p <- arg_parser("The Sorting Hat")
# Add a positional argument
p <- add_argument(p, "--orientation", 
                  help="Name of the person to sort", default=7)
# Add a flag
p <- add_argument(p, "--gender", 
                  help="enable debug mode", default=7)
# Add another flag
p <- add_argument(p, "--partnership",
                  help="output only the house", default=7)
# Add another flag
p <- add_argument(p, "--health",
                  help="output only the house", default=7)
argv <- parse_args(p)

# connect to database
# if you get "incomplete final line found" add \n as the last line
load_dot_env(file = "/home/mono/projects/python/prk/well-random/R/.env")

db <- Sys.getenv("POSTGRES_NAME")
host_db <- Sys.getenv("POSTGRES_HOST") 
db_port <- Sys.getenv("POSTGRES_PORT") 
db_user <- Sys.getenv("POSTGRES_USER") 
db_password <- Sys.getenv("POSTGRES_PASSWORD")

con <- dbConnect(RPostgres::Postgres(), 
                 dbname = db, 
                 host=host_db, 
                 port=db_port, 
                 user=db_user, 
                 password=db_password)  

# generate the matrix of covariate factors for the subjects
covmat_query <- dbSendQuery(con, "SELECT orientation, gender, partnership, health FROM arm_assigment")
covmat <- dbFetch(covmat_query)
dbClearResult(covmat_query)

# result is the treatment needed from minimization method
res_query <- dbSendQuery(con, "SELECT arm FROM arm_assigment")
res <- dbFetch(res_query)
dbClearResult(res_query)

# set trail variables
ntrt <- 4
nsample <- dim(res)[1] + 1
trtseq <- c(1, 2, 3, 4)
ratio <- c(3, 3, 2, 2)
# equal weights
covwt <- c(1/4, 1/4, 1/4, 1/4) 

# input
#argv <- parse_args(p, c("--orientation", "3",
#                        "--gender", "3", 
#                        "--partnership", "3", 
#                        "--health", "3"))
# ./arm_assigment.R --orientation 2 --gender 3 --partnership 2 --health 1

cov_df <- data.frame(orientation=argv$orientation, 
                      gender=argv$gender, 
                      partnership=argv$partnership, 
                      health=argv$health)

cov_final <- rbind(covmat, cov_df)

if (dim(res)[1] == 0)
{ res_assig <- 4 } else {
res_assig <- Minirand(covmat=data.matrix(cov_final), 
                      nsample,
                      covwt=covwt,
                      ratio=ratio, 
                      ntrt=ntrt, 
                      trtseq=trtseq, 
                      method="Range", 
                      result=data.matrix(res), 
                      p = 0.9)
}

dbWriteTable(con, 
             "arm_assigment", 
             data.frame(cov_df, 
                        arm=res_assig), 
             append = TRUE)

dbDisconnect(con)
# renv::snapshot()
cat(res_assig)