library(Minirand)
library(dotenv)
library(DBI)

db <- Sys.getenv("POSTGRES_NAME")
if (db == "") {
  load_dot_env(file = "./tests/.env")
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
                            "SELECT orientation, gender, partnership, health FROM pilot")
covmat <- dbFetch(covmat_query)
dbClearResult(covmat_query)

# set trail variables
ntrt <- 4
trtseq <- c(1, 2, 3, 4)
ratio <- c(3, 3, 2, 2)
# equal weights
covwt <- c(1 / 4, 1 / 4, 1 / 4, 1 / 4)

# result is the treatment needed from minimization method
res_query <- dbSendQuery(con,
                         "SELECT arm FROM pilot")
res <- dbFetch(res_query)
dbClearResult(res_query)

res1 <- unlist(res)

#Display the number of randomized subjects at covariate factors
balance1 <- randbalance(res1, covmat, ntrt, trtseq)
balance1
totimbal(trt = res1, covmat = covmat, covwt = covwt,
ratio = ratio, ntrt = ntrt, trtseq = trtseq, method = "Range")

