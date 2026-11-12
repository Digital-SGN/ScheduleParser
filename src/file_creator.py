import json

def save_schedule_to_file(schedule: dict, filename: str) -> None:
    """
    Сохраняет расписание в файл в формате JSON.

    Args:
        schedule: Словарь с расписанием.
        filename: Имя файла для сохранения.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(schedule, file, ensure_ascii=False, indent=4)