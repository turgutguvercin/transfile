Getting started

```

1) Run the Django development server
```powershell
python manage.py runserver
```

2) Start a Celery worker
- Windows (must use solo pool):
```powershell
celery --app translator.celery_app worker --loglevel=INFO --pool=solo
```


Notes
- Broker and backend default to `redis://127.0.0.1:6379/0` (see `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in `translator/settings.py`).
- If Redis is not running, Celery will fail to start. Adjust URLs if your Redis uses a different host/port/DB.
- Run the server and the Celery worker in separate terminals.