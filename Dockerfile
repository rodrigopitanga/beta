FROM python:2.7

ENV APP_HOME=/openbeta
RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

COPY requirements.txt .
RUN echo $(which python) && \
    virtualenv -p $(which python) venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    deactivate
COPY apiserver/*.py apiserver/
COPY docker-start.sh .

EXPOSE 8000

CMD ["bash", "-c", "${APP_HOME}/docker-start.sh" ]