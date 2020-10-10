library(Minirand)
library(dotenv)
library(DBI)
library(renv)

# renv::init()
# renv::restore()

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
cov_new <- c(0, 2, 1, 1) 
cov_new <- rbind(c(0, 2, 1, 1))
colnames(cov_new) = c("orientation", "gender", "partnership", "health") 

cov_final <- rbind(covmat, cov_new)

if (dim(res)[1] == 0)
{  } else {
res_assig <- Minirand(covmat=cov_final, 
                      nsample,
                      covwt=covwt,
                      ratio=ratio, 
                      ntrt=ntrt, 
                      trtseq=trtseq, 
                      method="Range", 
                      result=res, 
                      p = 0.9)
}


dbDisconnect(con)
# renv::snapshot()
