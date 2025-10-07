FROM python:3.11-slim
WORKDIR /app
COPY generator.py /app/generator.py
RUN pip install requests faker
CMD ["python", "generator.py"]
