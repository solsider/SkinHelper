# College Portal (Frontend + Backend)

Современный сайт колледжа в сине-белой гамме с полноценной backend-логикой.

## Стек
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Backend**: FastAPI, SQLAlchemy, SQLite, JWT

## Структура проекта

```text
college_site/
  backend/
    app/
      main.py
      database.py
      models.py
      schemas.py
      auth.py
      deps.py
      seed.py
      routers/
        auth.py
        public.py
        student.py
        admin.py
    requirements.txt
  frontend/
    index.html
    css/styles.css
    js/app.js
    pages/
      about.html
      specialties.html
      applicants.html
      news.html
      schedule.html
      teachers.html
      contacts.html
      student-cabinet.html
      login.html
      admin.html
      404.html
```

## Запуск локально

```bash
cd college_site/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте: `http://localhost:8000`

## Демо-аккаунты
- Администратор: `admin@college.local` / `admin123`
- Студент: `student@college.local` / `student123`
- Преподаватель: `teacher@college.local` / `teacher123`

## Реализовано
- Регистрация/авторизация JWT, роли (student/teacher/admin)
- Подача заявки на поступление
- CRUD API для новостей, расписания, специальностей, преподавателей (admin)
- Личный кабинет студента
- Админ-панель (веб-форма + API)
- Адаптивный интерфейс, hover-эффекты, плавные анимации
- Страница 404
- Тестовые данные для новостей/преподавателей/специальностей/расписания/контактов
