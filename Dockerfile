FROM rstudio/plumber

# Install python dependencies
WORKDIR /code/
RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install pipenv
COPY python /code/
RUN pipenv --python 3 install

# Install R dependencies
RUN R -e "install.packages('Minirand',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('dotenv',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('DBI',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('sodium',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('plumber',dependencies=TRUE, repos='http://cran.rstudio.com/')"

COPY R /code/
COPY ./entrypoint.sh /code/

ENTRYPOINT ["/code/entrypoint.sh"]
