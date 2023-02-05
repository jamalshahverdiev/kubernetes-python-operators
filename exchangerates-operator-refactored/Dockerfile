# FROM docker.io/python:3.10 AS builder
# RUN pip install --user pipenv
# # Tell pipenv to create venv in the current directory
# ENV PIPENV_VENV_IN_PROJECT=1
# ADD Pipfile.lock Pipfile /usr/src/
# WORKDIR /usr/src
# RUN /root/.local/bin/pipenv sync

# FROM docker.io/python:3.10 AS runtime
# RUN mkdir -v /usr/src/venv
# COPY --from=builder /usr/src/.venv/ /usr/src/venv/
# WORKDIR /usr/src/
# COPY src ./src
# COPY exchangerates-operator.py .
# ENTRYPOINT ["./venv/bin/python", "-u"]
# CMD ["exchangerates-operator.py"]

FROM python:3.8-alpine
RUN apk --update add gcc build-base
RUN pip install --no-cache-dir kopf kubernetes requests
WORKDIR /usr/src/
COPY exchangerates-operator.py /
ENTRYPOINT [ "kopf", "run" ]
CMD ["/exchangerates-operator.py"]