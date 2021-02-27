#!/usr/bin/env Rscript

library(Minirand)
library(dotenv)
library(DBI)
library(sodium)
library(plumber)

# curl -X POST "http://localhost:8787/p/af16c9bd/arm?orientation=2&gender=2&partnership=1&health=2" -H  "accept: */*" -d ""

#* Return arm allocation
#* @post /arm
function(orientation = 100, gender = 100, partnership = 100, health = 100) {
  # connect to database
  # if you get "incomplete final line found" add \n as the last line
  db <- Sys.getenv("POSTGRES_NAME")
  if (db == "") {
    load_dot_env(file = ".env")
  }
  db <- Sys.getenv("POSTGRES_NAME")
  host_db <- Sys.getenv("POSTGRES_HOST")
  db_port <- Sys.getenv("POSTGRES_PORT")
  db_user <- Sys.getenv("POSTGRES_USER")
  db_password <- Sys.getenv("POSTGRES_PASSWORD")

  con <- dbConnect(RPostgres::Postgres(),
                   dbname = db,
                   host = host_db,
                   port = db_port,
                   user = db_user,
                   password = db_password)

  # generate the matrix of covariate factors for the subjects
  covmat_query <- dbSendQuery(con,
                              "SELECT orientation, gender, partnership, health FROM arm_assigment")
  covmat <- dbFetch(covmat_query)
  dbClearResult(covmat_query)

  # result is the treatment needed from minimization method
  res_query <- dbSendQuery(con,
                           "SELECT arm FROM arm_assigment")
  res <- dbFetch(res_query)
  dbClearResult(res_query)

  # set trial variables
  ntrt <- 4
  nsample <- dim(res)[1] + 1
  trtseq <- c(1, 2, 3, 4)
  ratio <- c(3, 3, 2, 2)
  # equal weights
  covwt <- c(1 / 4, 1 / 4, 1 / 4, 1 / 4)

  cov_df <- data.frame(orientation = orientation,
                       gender = gender,
                       partnership = partnership,
                       health = health)

  cov_final <- rbind(covmat, cov_df)

  if (dim(res)[1] == 0)
  { res_assig <- 4 } else {
    res_assig <- Minirand(covmat = data.matrix(cov_final),
                          nsample,
                          covwt = covwt,
                          ratio = ratio,
                          ntrt = ntrt,
                          trtseq = trtseq,
                          method = "Range",
                          result = data.matrix(res),
                          p = 0.9)
  }

  dbWriteTable(con,
               "arm_assigment",
               data.frame(cov_df,
                          arm = res_assig),
               append = TRUE)

  dbDisconnect(con)
  output <- res_assig
  return(output)
}