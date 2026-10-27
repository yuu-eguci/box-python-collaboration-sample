FROM python:3.14-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIPENV_VENV_IN_PROJECT=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install pipenv==2026.10.3 && useradd --create-home app
WORKDIR /app
RUN chown app /app
USER app

COPY --chown=app Pipfile Pipfile.lock ./
RUN pipenv sync --dev

COPY --chown=app . .

CMD ["pipenv", "run", "pytest"]
