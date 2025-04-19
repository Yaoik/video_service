## Getting started

1. Создайте файл `.env` в корневой директории проекта
```bash
cp .env.template .env
```
2. Запустите приложение

```bash
docker-compose down -v & docker-compose up --build
```
3. Выполните миграцию базы данных
```bash
docker-compose exec django python manage.py makemigrations & docker-compose exec django python manage.py migrate & docker-compose exec django python manage.py collectstatic --noinput & docker-compose exec django python manage.py createsuperuser --username admin --email admin@gmail.com --noinput
```
4. Некоторые полезные страницы
   * Админка - http://localhost:8000/admin/
   * API документация
     * Swagger - http://localhost:8000/api/schema/swagger-ui/
     * Redoc - http://localhost:8000/api/schema/redoc/
