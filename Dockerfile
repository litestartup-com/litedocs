FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY litedocs/ litedocs/
COPY README.md .

RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENTRYPOINT ["litedocs", "serve"]
CMD ["--host", "0.0.0.0", "--port", "8000", "/docs"]
