# Title     : TODO
# Objective : TODO
# Created by: mono
# Created on: 2021/02/27

library(Minirand)

ntrt <- 4
nsample <- 1000
# T1, T2, BAU, PC
trtseq <- c(1, 2, 3, 4)
# ratio <- c(3, 3, 2, 2)
ratio <- c(1,1,1,1)
# gender
c1 <- sample(c(0, 1, 2, 3),
             nsample,
             replace = TRUE,
             prob = c(0.33, 0.33, 0.2, 0.2))
# orientation
c2 <- sample(c(0, 1, 2, 3),
             nsample,
             replace = TRUE,
             prob = c(0.33, 0.33, 0.2, 0.2))
# partnership
c3 <- sample(c(0, 1, 2),
             nsample,
             replace = TRUE,
             prob = c(0.33, 0.2, 0.5))
# health
c4 <- sample(c(0, 1, 2),
             nsample,
             replace = TRUE,
             prob = c(0.33, 0.2, 0.5))
# generate the matrix of covariate factors for the subjects
covmat <- cbind(c1, c2, c3, c4)

# label of the covariates
colnames(covmat) <- c("gender", "orientation",
                      "partnership",
                      "health")

# equal weights
covwt <- c(1/4, 1/4, 1/4, 1/4)
# result is the treatment needed from minimization method
res <- rep(100, nsample)

# gernerate treatment assignment for the 1st subject
res[1] <- sample(trtseq, 1, replace = TRUE, prob = ratio/sum(ratio))

for (j in 2:nsample)
{
  # get treatment assignment sequentiall for all subjects
  res[j] <- Minirand(covmat=covmat, j, covwt=covwt, ratio=ratio,
                     ntrt=ntrt, trtseq=trtseq, method="Range", result=res,
                     p = 0.9)
}

trt1 <- res
#Display the number of randomized subjects at covariate factors
balance1 <- randbalance(trt1, covmat, ntrt, trtseq)

totimbal(trt = trt1, covmat = covmat, covwt = covwt,
         ratio = ratio, ntrt = ntrt, trtseq = trtseq, method = "Range")
