# farming-prod-online
 

## 📊 База данных

Проект использует SQLite в качестве базы данных и SQLAlchemy для ORM. Структура базы данных:
- Users (пользователи)
- Products (продукты)
- Categories (категории)
- Orders (заказы)
- Reviews (отзывы)
- ActivityLog (журнал действий)

## 👥 Роли пользователей

- **user**: базовая роль
- **seller**: расширенные возможности для продажи
- **admin**: полный доступ к системе

## Админка

- email: admin@mail.ru
- password: admin

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Demi-Play/farming-prod-online.git
```

Или просто скачайте архивом распаковав в удобную для вас дирректорию

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите проект:

```bash
python app.py
```


4. Перейдите в браузер и откройте:

```bash
http://localhost:5000
```


В будущем, когда вы будете вносить изменения в модели (например, добавлять новые поля или изменять существующие), вы можете:
Создать новую миграцию: flask --app run.py db migrate -m "Описание изменений"
Применить миграцию: flask --app run.py db upgrade
Также вы можете:
Откатить последнюю миграцию: flask --app run.py db downgrade
Посмотреть историю миграций: flask --app run.py db history
Посмотреть текущую версию: flask --app run.py db current