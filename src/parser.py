import datetime
from tqdm import tqdm
from enums import DayOfWeek


def lesson_to_dict(
    lesson: dict,
    date: datetime.date,
    day_of_week: DayOfWeek,
    teachers: list[str],
    group_name: str,
    audiences: list[str],
) -> dict:
    """
    Собирает плоский словарь занятия для сохранения в файл.

    Args:
        lesson: Сырые данные занятия из API LKS.
        date: Календарная дата занятия.
        day_of_week: День недели.
        teachers: ФИО преподавателей.
        group_name: Название учебной группы.
        audiences: Названия аудиторий.

    Returns:
        Словарь с полями ``date``, ``group_name``, ``discipline``,
        ``start_time``, ``end_time``, ``teachers``, ``audiences``,
        ``lesson_type``, ``week_type``, ``day_of_week``.
    """
    return {
        'date': date.isoformat(),
        'group_name': group_name,
        'discipline': lesson['discipline']['fullName'],
        'start_time': lesson['startTime'],
        'end_time': lesson['endTime'],
        'teachers': teachers,
        'audiences': audiences,
        'lesson_type': lesson['discipline'].get('actType') or 'other',
        'week_type': lesson['week'],
        'day_of_week': day_of_week.value,
    }


def get_date(
        week_number: int,
        day_of_week: DayOfWeek,
        start_date: datetime.date
) -> datetime.date:
    """
    Вычисляет календарную дату занятия.

    Args:
        week_number: Номер учебной недели.
        day_of_week: День недели занятия.
        start_date: Дата начала семестра.

    Returns:
        Дата занятия.
    """
    days_to_add = (
        (week_number - 1) * 7
        + (day_of_week.value - start_date.isoweekday())
    )

    return start_date + datetime.timedelta(days=days_to_add)


def get_teachers(lesson: dict) -> list[str]:
    """
    Извлекает ФИО преподавателей из сырых данных занятия.

    Args:
        lesson: Сырые данные занятия из API LKS.

    Returns:
        Список строк вида ``"Имя Отчество Фамилия"``.
    """
    return [
        f'{t["firstName"]} {t["middleName"]} {t["lastName"]}'
        for t in lesson.get('teachers', [])
    ]


def get_audiences(lesson: dict) -> list[str]:
    """
    Извлекает названия аудиторий из сырых данных занятия.

    Args:
        lesson: Сырые данные занятия из API LKS.

    Returns:
        Список названий аудиторий, пустой список, если аудитория не назначена.
    """
    return [a['name'] for a in lesson.get('audiences', [])]


def parse_schedule(
        schedule: dict,
        week_numbers: int,
        start_date: datetime.date
) -> list[dict]:
    """
    Разворачивает расписание групп в плоский список занятий с датами.

    Args:
        schedule: ``{название_группы: список_занятий}``.
        week_numbers: Сколько недель разворачивать.
        start_date: Дата начала семестра.

    Returns:
        Список занятий — по одному словарю на каждое занятие.

    Raises:
        ValueError: В данных занятия встретился неизвестный ``day``.
        KeyError: В данных занятия нет обязательного поля.
    """
    lessons: list[dict] = []

    for group_name, group_schedule in tqdm(
        schedule.items(),
        desc='Нормализация',
        unit='гр',
    ):
        for lesson in group_schedule:
            day_of_week = DayOfWeek(lesson['day'])
            teachers = get_teachers(lesson)
            week_type = lesson['week']
            audiences = get_audiences(lesson)

            if week_type == 'all':
                week_starter, week_jumper = 0, 1
            elif week_type == 'zn':
                week_starter, week_jumper = 1, 2
            else:  # 'ch'
                week_starter, week_jumper = 0, 2

            for i in range(week_starter, week_numbers, week_jumper):
                if i == 0 and start_date.isoweekday() > day_of_week.value:
                    continue

                date = get_date(i + 1, day_of_week, start_date)
                lessons.append(lesson_to_dict(
                    lesson, date, day_of_week, teachers, group_name, audiences,
                ))

    lessons.sort(key=lambda x: (
        x['group_name'],
        x['date'],
        x['start_time'],
    ))

    return lessons
