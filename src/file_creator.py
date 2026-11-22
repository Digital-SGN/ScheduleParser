import csv
import json
from pathlib import Path


def save_schedule(schedule: list[dict], filename: str | Path) -> None:
    """
    Сохраняет список занятий в файл

    Args:
        schedule: Список занятий.
        filename: Путь к файлу, формат выбирается по расширению: ``.csv``- CSV, иначе JSON.

    Raises:
        OSError: Не удалось создать каталог или записать файл.
    """
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == '.csv':
        _save_as_csv(schedule, path)
    else:
        _save_as_json(schedule, path)


def _save_as_json(schedule: list[dict], path: Path) -> None:
    """Сохраняет расписание в JSON"""
    with path.open('w', encoding='utf-8') as file:
        json.dump(schedule, file, ensure_ascii=False, indent=4)


def _save_as_csv(schedule: list[dict], path: Path) -> None:
    if not schedule:
        path.write_text('', encoding='utf-8')
        return

    fieldnames = list(schedule[0].keys())
    with path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for lesson in schedule:
            row = dict(lesson)

            if isinstance(row.get('teachers'), list):
                row['teachers'] = '; '.join(row['teachers'])

            if isinstance(row.get('audiences'), list):
                row['audiences'] = '; '.join(
                    f"{a['name']}|{a.get('building_id') or ''}|{a.get('building') or ''}"
                    for a in row['audiences']
                )

            writer.writerow(row)
