# CAPAS live engine — serves the static site (docs/) + POST /api/{gate,reward,decide,certificate}
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir numpy scipy
ENV PORT=7860
# hosted mode: refuse to start without CAPAS_API_KEY and a private CAPAS_SIGNING_SECRET (incident 2026-10-14)
ENV CAPAS_HOSTED=1
EXPOSE 7860
CMD ["python", "capas_api.py"]
