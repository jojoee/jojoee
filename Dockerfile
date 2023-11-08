FROM python:3.7.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./module /code/module
COPY ./precompute /code/precompute

VOLUME /code/precompute

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
