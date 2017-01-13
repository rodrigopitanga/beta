FROM python:2.7

ENV APP_HOME=/openbeta
RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apiserver/*.py apiserver/
COPY docker-start.sh .

EXPOSE 8000

CMD ["bash", "-c", "${APP_HOME}/docker-start.sh" ]