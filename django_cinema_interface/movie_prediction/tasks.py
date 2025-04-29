# tasks.py
from celery import shared_task
from subprocess import Popen, PIPE

@shared_task
def run_scrapy_task():
    command = "scrapy crawl newreleasespider LOG_LEVEL=INFO"
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        return {"status": "success", "message": "Scraping started successfully."}
    else:
        return {"status": "error", "message": f"Error starting scraping: {stderr.decode()}"}
