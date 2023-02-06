FROM python:3.9
COPY requirements.txt dbwriter-operator.py ./
RUN pip install -r requirements.txt
COPY src ./src
ENTRYPOINT ["kopf", "run"]
CMD ["dbwriter-operator.py"]
