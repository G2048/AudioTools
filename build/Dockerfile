FROM python:3.12.7-bookworm AS python-base

# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1\
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    ca-certificates

RUN update-ca-certificates
RUN curl -ksSL https://install.python-poetry.org | python3 -

# final stage
FROM python-base AS final
RUN apt-get install ffmpeg -y
RUN apt install git-lfs -y && git lfs install
# RUN git clone https://huggingface.co/openai/whisper-medium

WORKDIR /server-audio
VOLUME /whisper
COPY whisper-medium/ whisper

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root
COPY app /server-audio/app

CMD ["python", "-m", "app.main"]
