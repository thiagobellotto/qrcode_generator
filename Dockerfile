# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

EXPOSE 8501

## To make things easier when running the rest of our commands, let’s create a working directory. 
## This instructs Docker to use this path as the default location for all subsequent commands. 
## By doing this, we do not have to type out full file paths but can use relative paths based on the working directory.
WORKDIR /app

## We’ll use the COPY command to do this. The COPY command takes two parameters. 
## The first parameter tells Docker what file(s) you would like to copy into the image. 
## The second parameter tells Docker where you want that file(s) to be copied to. 
## We’ll copy the requirements.txt file into our working directory /app
COPY requirements.txt requirements.txt

##  This works exactly the same as if we were running pip3 install locally on our machine, 
## but this time the modules are installed into the image.
RUN pip3 install -r requirements.txt

## At this point, we have an image that is based on Python version 3.8 and we have installed our dependencies. 
## The next step is to add our source code into the image. 
## We’ll use the COPY command just like we did with our requirements.txt file above.
COPY . /app

## Now, all we have to do is to tell Docker what command we want to run when our image is executed inside a container. 
## We do this using the CMD command. 
## Note that we need to make the application externally visible (i.e. from outside the container) by specifying --host=0.0.0.0.
CMD ["streamlit", "run", "streamlit_qrcode.py", "--server.port=8501"]