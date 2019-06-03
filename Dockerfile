FROM python:3

RUN apt-get update && apt-get install -y git ffmpeg
COPY . .
RUN python -m pip install -r requirements.txt
RUN python db_init.py

EXPOSE 8000
CMD ["gunicorn", "app:app", "-b :8000"]
