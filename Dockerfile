FROM python:3.11.8-bookworm
LABEL authors="elgatoafk"

WORKDIR /helper-bot

RUN curl -sSL https://install.python-poetry.org | python3 -


ENV PATH="${PATH}:/root/.local/bin"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "python", "-m", "main"]

