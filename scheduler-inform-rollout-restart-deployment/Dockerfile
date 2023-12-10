FROM python:3.12-alpine as builder
WORKDIR /app
RUN pip install pipenv && pip install --upgrade pip
COPY Pipfile Pipfile.lock ./
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY deploy-scheduler.py ./
COPY src ./src
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["python"]
CMD ["deploy-scheduler.py"]
