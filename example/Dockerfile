FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
ENV POETRY_VERSION=1.1.6
ENV PYTHONPATH=/app/
ENV APP_MODULE=main:app

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./main.py /app/

RUN pip install --upgrade pip && \ 
  pip install "poetry==$POETRY_VERSION" && \
  poetry config virtualenvs.create false && \
  poetry install --no-root
