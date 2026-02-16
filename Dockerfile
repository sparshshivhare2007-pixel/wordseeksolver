FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN curl -o commonWords.json "https://raw.githubusercontent.com/dwyl/english-words/master/words_5_alpha.txt"
CMD ["python", "run.py"]
