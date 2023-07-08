FROM python:3.9
COPY requirements.txt ./ 
RUN pip install -r requirements.txt
COPY deploy-scheduler.py ./
COPY src ./src
ENTRYPOINT ["python"]
CMD ["deploy-scheduler.py"]