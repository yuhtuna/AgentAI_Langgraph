
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN if grep -q "pywin32" requirements.txt; then sed -i '/pywin32/d' requirements.txt; fi
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
