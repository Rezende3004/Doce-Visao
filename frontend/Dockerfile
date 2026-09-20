FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir streamlit httpx plotly pandas

COPY frontend/ .

ENV PYTHONUNBUFFERED=1
ENV DOCEVISAO_API_URL=http://backend:8000

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
