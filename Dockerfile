FROM python:3.12
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-root
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
