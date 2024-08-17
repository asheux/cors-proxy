FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        git gcc curl netcat-traditional curl libjpeg-dev \
        libgl1-mesa-glx ibglib2.0-0 libsm6 libxrender1 libxext6

# Python won't try to write .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# ensures our console output looks familiar and is not buffered by Docker
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN python -m pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

# Copy project
COPY . /code/

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENV FLASK_ENV=development

# Define environment variable
ENV FLASK_APP=proxy.py

RUN ["chmod", "+x", "/code/entrypoint.sh"]

ENTRYPOINT ["/code/entrypoint.sh"]
