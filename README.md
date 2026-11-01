# Эне-Сай — сайт салона + CRM-бот

Django-сайт с онлайн-записью. Заявки приходят в закрытый Telegram-бот (вход по паролю).

## Локальный запуск
```bash
pip install -r requirements.txt
python manage.py runserver
```
Одна команда: создаёт базу, администратора сайта (из `.env`), запускает бота и сайт.
Сайт: http://127.0.0.1:8000 · Админка: http://127.0.0.1:8000/admin/ (логин и пароль — `DJANGO_ADMIN_USER` / `DJANGO_ADMIN_PASSWORD` в `.env`).
В боте: `/start` → пароль → заявки приходят сюда. `/bookings` — последние 10, `/logout` — выйти.

## Настройка
Все секреты в `.env` (в git не попадает). Шаблон — `.env.example`. Услуги и цены редактируются в `/admin/`.

## Деплой через GitHub
1. `git init && git add . && git commit -m "init"`, затем push в репозиторий (`.env` игнорируется).
2. На сервере: `git pull`, создать `.env` по образцу, затем
   `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`.
3. Запуск: `gunicorn config.wsgi` для сайта и `python manage.py run_bot` для бота (на сервере с gunicorn бот не стартует сам — запускайте его отдельным процессом: systemd, supervisor или Procfile).
4. В `.env` на сервере: `DEBUG=False`, `ALLOWED_HOSTS=ваш-домен`, `CSRF_TRUSTED_ORIGINS=https://ваш-домен`, длинный `SECRET_KEY`.
