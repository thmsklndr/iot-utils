ARG python_version=3.10

FROM python:${python_version}-slim
ARG python_version

LABEL org.opencontainers.image.authors="kleinoeder@time4oss.de"
LABEL org.opencontainers.image.vendor="time4oss"
LABEL org.opencontainers.image.version="20231031"

ENV \
  DEBIAN_FRONTEND=noninteractive \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHON_VERSION_MAJOR_MINOR=${python_version} \
  # py-poetry:
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_VIRTUALENVS_IN_PROJECT=false

ENV BUILD_ONLY_PACKAGES="build-essential libssl-dev gettext git"

WORKDIR /opt/iot_utils

COPY ./ /opt/iot_utils

RUN set -eux \
  && apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    tini ${BUILD_ONLY_PACKAGES} \
  && pip install -U pip ; pip install poetry \
  && poetry install \
  && apt-get purge -y \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false ${BUILD_ONLY_PACKAGES} \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/bin/tini", "--" ]

CMD [ "python" ]

WORKDIR /app
