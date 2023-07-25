FROM python:3.9
COPY requirements.txt ./ 
RUN pip install -r requirements.txt
COPY kyverno-operator.py ./
COPY templates ./templates
COPY src ./src
ENTRYPOINT ["kopf", "run"]
CMD ["kyverno-operator.py"]