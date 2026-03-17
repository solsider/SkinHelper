from .auth import hash_password
from .models import Contact, News, Schedule, Specialty, Teacher, User


def seed_data(db):
    if not db.query(User).first():
        db.add_all(
            [
                User(full_name="Администратор", email="admin@college.local", hashed_password=hash_password("admin123"), role="admin"),
                User(full_name="Иван Петров", email="student@college.local", hashed_password=hash_password("student123"), role="student"),
                User(full_name="Ольга Смирнова", email="teacher@college.local", hashed_password=hash_password("teacher123"), role="teacher"),
            ]
        )

    if not db.query(Specialty).first():
        db.add_all(
            [
                Specialty(title="Разработка ПО", code="09.02.07", duration="3 года 10 мес", description="Подготовка backend/frontend разработчиков."),
                Specialty(title="Информационная безопасность", code="10.02.05", duration="3 года 10 мес", description="Защита данных и инфраструктуры."),
                Specialty(title="Сетевое администрирование", code="09.02.06", duration="3 года 10 мес", description="Проектирование и поддержка сетей."),
            ]
        )

    if not db.query(Teacher).first():
        db.add_all(
            [
                Teacher(full_name="Наталья Фролова", position="Преподаватель Python", bio="10+ лет опыта в промышленной разработке.", email="frolova@college.local"),
                Teacher(full_name="Дмитрий Орлов", position="Преподаватель сетевых технологий", bio="Сертифицированный инженер Cisco.", email="orlov@college.local"),
            ]
        )

    if not db.query(News).first():
        db.add_all(
            [
                News(title="Открытие нового IT-лаборатории", summary="Современные рабочие станции и сетевое оборудование.", content="В колледже запущена новая лаборатория для практических занятий."),
                News(title="День открытых дверей", summary="Приглашаем абитуриентов и родителей.", content="Программа включает экскурсию, мастер-классы и консультации."),
            ]
        )

    if not db.query(Schedule).first():
        db.add_all(
            [
                Schedule(group_name="П-101", day_of_week="Понедельник", lesson_time="09:00-10:30", subject="Алгоритмы", teacher="Н. Фролова", room="204"),
                Schedule(group_name="П-101", day_of_week="Вторник", lesson_time="10:45-12:15", subject="Сети", teacher="Д. Орлов", room="105"),
            ]
        )

    if not db.query(Contact).first():
        db.add(
            Contact(
                address="г. Москва, ул. Академическая, 10",
                phone="+7 (495) 123-45-67",
                email="info@college.local",
                map_embed="https://maps.google.com/?q=Moscow",
            )
        )

    db.commit()
