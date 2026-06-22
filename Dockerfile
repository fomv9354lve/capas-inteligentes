# CAPAS live engine — serves the static site (docs/) + POST /api/{gate,reward,decide,certificate}
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir numpy
ENV PORT=7860
EXPOSE 7860
CMD ["python", "capas_api.py"]
