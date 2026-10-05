FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ZAWAMEKI_DB=/data/zawameki.sqlite3 \
    ZAWAMEKI_PORT=8100

LABEL org.opencontainers.image.title="Zawameki" \
      org.opencontainers.image.description="講義中の理解度・コメント・質問をリアルタイムに集める Web アプリ" \
      org.opencontainers.image.source="https://github.com/koide55/CompOutline"

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY zawameki ./zawameki

RUN useradd --system --uid 10001 zawameki && mkdir -p /data && chown zawameki /data
USER zawameki
VOLUME /data
EXPOSE 8100

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8100/healthz', timeout=3).read()"

CMD ["python", "-m", "zawameki"]
