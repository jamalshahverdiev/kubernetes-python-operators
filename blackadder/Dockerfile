FROM docker.io/python:3.10 AS builder
RUN pip install --user pipenv
ENV PIPENV_VENV_IN_PROJECT=1
ADD Pipfile.lock Pipfile /usr/src/
WORKDIR /usr/src
RUN /root/.local/bin/pipenv sync

FROM docker.io/python:3.10 AS runtime
RUN mkdir -v /usr/src/venv
COPY --from=builder /usr/src/.venv/ /usr/src/venv/
WORKDIR /usr/src/
COPY src ./src
COPY refactored-controller.py .
ENTRYPOINT ["./venv/bin/python", "-u"]
CMD ["refactored-controller.py"]
