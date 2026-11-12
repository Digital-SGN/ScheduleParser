import datetime
from tqdm import tqdm

from enums import DayOfWeek


def lesson_to_dict(
    lesson: dict,
    date: datetime.date,
    day_of_week: DayOfWeek,
    teachers: list,
    group_name: str,
    audiences: list
) -> dict:
    """
    Преобразует информацию о занятии в словарь.

    Args:
        lesson: Исходные данные о занятии.
        date: Дата проведения занятия.
        day_of_week: День недели.
        teachers: Список преподавателей.
        group_name: Название учебной группы.
        audiences: Список аудиторий.

    Returns:
        Словарь с обработанной информацией о занятии.
    """
    return {
        'date': date.isoformat(),
        'group_name': group_name,
        'discipline': lesson['discipline']['fullName'],
        'start_time': lesson['startTime'],
        'end_time': lesson['endTime'],
        'teachers': teachers,
        'audiences': audiences,
        'lesson_type': lesson['discipline'].get('actType'),
        'week_type': lesson['week'],
        'day_of_week': day_of_week,
    }


def get_date(
    week_number: int,
    day_of_week: DayOfWeek,
    start_date: datetime.date
) -> datetime.date:
    """
    Вычисляет дату занятия на основе номера учебной недели.

    Args:
        week_number: Номер учебной недели.
        day_of_week: День недели проведения занятия.
        start_date: Дата начала семестра.

    Returns:
        Дата проведения занятия.
    """
    days_to_add = (
        (week_number - 1) * 7
        + (day_of_week.value - start_date.isoweekday())
    )
    return start_date + datetime.timedelta(days=days_to_add)


def get_teachers(lesson: dict) -> list:
    """
    Извлекает список преподавателей из данных о занятии.

    Args:
        lesson: Исходные данные о занятии.

    Returns:
        Список полных имён преподавателей.
    """
    return [
        f'{teacher["firstName"]} {teacher["middleName"]} {teacher["lastName"]}'
        for teacher in lesson['teachers']
    ]


def get_audiences(lesson: dict) -> list:
    """
    Извлекает список аудиторий из данных о занятии.

    Args:
        lesson: Исходные данные о занятии.

    Returns:
        Список названий аудиторий.
    """
    return [
        audience['name']
        for audience in lesson.get('audiences', [])
    ]


def parse_schedule(
    schedule: dict,
    week_numbers: int,
    start_date: datetime.date
) -> list:
    """
    Преобразует расписание учебных групп в список отдельных занятий.

    Обрабатывает занятия с учётом их типа недели и вычисляет даты
    проведения на основе начала семестра.

    Args:
        schedule: Словарь расписаний, где ключ — название группы,
            а значение — список её занятий.
        week_numbers: Количество учебных недель для обработки.
        start_date: Дата начала семестра.

    Returns:
        Список словарей с обработанными занятиями.
    """
    lessons = []

    for group_name, group_schedule in tqdm(
        schedule.items(),
        desc="Обработка групп",
        unit="группа"
    ):
        for lesson in group_schedule:
            day_of_week = DayOfWeek(lesson['day'])
            teachers = get_teachers(lesson)
            week_type = lesson['week']
            audiences = get_audiences(lesson)

            if week_type == 'all':
                week_starter = 0
                week_jumper = 1
            else:
                week_starter = 1 if week_type == 'zn' else 0
                week_jumper = 2

            for i in range(week_starter, week_numbers, week_jumper):
                if i != 0 or start_date.isoweekday() <= day_of_week.value:
                    date = get_date(i + 1, day_of_week, start_date)
                    lesson_dict = lesson_to_dict(
                        lesson,
                        date,
                        day_of_week,
                        teachers,
                        group_name,
                        audiences
                    )
                    lessons.append(lesson_dict)

    return lessons