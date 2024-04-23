# FROM
FROM python:latest

# WORKDIR
WORKDIR /code

# COPY
COPY ./requirements.txt /code/requirements.txt

# RUN
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY
COPY / /code/app

# CMD 
CMD ["uvicorn", "app.main:app", "--reload",  "--host", "0.0.0.0", "--port", "80"]