FROM python:3.12
COPY requirements.txt ./ 
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY operator.py ./
COPY templates ./templates
COPY src ./src
ENTRYPOINT ["kopf", "run"]
CMD ["operator.py"]