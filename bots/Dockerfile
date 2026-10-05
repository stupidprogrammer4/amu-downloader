FROM python:3.13.16-slim-bookworm@sha256:5024f48ba9441d4b13a95d3945abc6365538e3a31109833367a1923523c6efed
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpcre2-8-0 perl-base \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libpcre2-8-0)" ge 10.42-1+deb12u2 \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' perl-base)" ge 5.36.0-7+deb12u4 \
    && rm -rf /var/lib/apt/lists/*
COPY bots/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock
COPY packages/contracts /app/packages/contracts
COPY bots /app/bots
RUN pip install --no-cache-dir --no-deps ./packages/contracts ./bots \
    && useradd --create-home --uid 10001 downloader
RUN python -m pip check \
    && python -c "from downloader_bot.runtime import DownloaderRuntime" \
    && python -m pip uninstall -y setuptools pip \
    && rm -rf /usr/local/lib/python3.13/ensurepip
USER downloader
LABEL org.opencontainers.image.source="https://github.com/stupidprogrammer4/amu-downloader"
CMD ["python", "-m", "downloader_bot.runtime"]
