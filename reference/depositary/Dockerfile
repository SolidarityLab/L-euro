# SPDX-License-Identifier: EUPL-1.2
# Build from the repository root:
#   docker build -f reference/depositary/Dockerfile .
FROM python:3.13-slim
RUN useradd --system --uid 10001 leuro
WORKDIR /srv
COPY reference/depositary/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY schemas/ /srv/schemas/
COPY reference/depositary/app/ /srv/app/
ENV LEURO_SCHEMAS=/srv/schemas PYTHONUNBUFFERED=1
USER leuro
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/v0/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
