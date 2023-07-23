FROM python:3.11-slim
WORKDIR /app
RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy
COPY certs/ /app/certs
COPY src/ /app/src
COPY main.py /app/main.py
EXPOSE 443
CMD ["python", "main.py"]
