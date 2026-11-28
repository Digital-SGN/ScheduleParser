<p align="center">
  <img width="160" src="https://github.com/Digital-SGN/Handbook/blob/main/assets/logo_schedule_parser.png" alt="Логотип" />
</p>

<h1 align="center"> Парсер расписания </h1> 
<p align="center">
  Скрипт для сбора, нормализации и сохранения расписания МГТУ им. Баумана (LKS) в удобный файл.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/JSON%20%2F%20CSV-format-000000?style=flat-square&logo=json&logoColor=white" />
  <img src="https://img.shields.io/badge/LKS-API-0CBFA1?style=flat-square" />
</p>

## О проекте

Сырые данные из API LKS сложны для обработки: в них нет прямых календарных дат, есть сложная структура факультетов, а информация об аудиториях приходит в специфичном формате.

Скрипт решает три задачи:

- <img src="https://cdn.simpleicons.org/python/0CBFA1" width="16" /> **Сбор данных:** параллельно забирает расписание через публичный API LKS.
- <img src="https://cdn.simpleicons.org/json/0CBFA1" width="16" /> **Нормализация:** превращает сырые дни недели в реальные календарные даты, а UUID аудиторий — в понятные номера.
- <img src="https://cdn.simpleicons.org/databricks/0CBFA1" width="16" /> **Сохранение:** выгружает готовые данные в JSON или CSV.

## Архитектура
<img width="2200" height="1440" src="https://github.com/Digital-SGN/Handbook/blob/main/assets/schedule-parser-architecture_1.png" />

## Установка

```bash
git clone https://github.com/Digital-SGN/ScheduleParser
cd ScheduleParser

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка `src/settings.py`

| Параметр | По умолчанию | Описание |
|---|---|---|
| `FILIAL` | `8c1b7... (головной вуз)` | UUID филиала (см. `/structure` в API LKS) |
| `START_DATE` | `2026-09-01` | Дата начала семестра, `YYYY-MM-DD` |
| `WEEKS` | `17` | Сколько недель разворачивать |
| `OUTPUT` | `schedule.json` | Выходной файл (`.json` или `.csv`) |
| `WORKERS` | `16` | Потоков параллельных запросов |
| `TIMEOUT` | `30` | Таймаут одного запроса, сек |
| `VERBOSE` | `False` | Подробные логи (уровень DEBUG) |

## Запуск
```bash
python src/main.py
```

Пример вывода:

```text
Парсер расписания МГТУ им. Баумана
Филиал: 8c1b7b...  |  Старт: 2026-09-01  |  недель: 17  |  потоков: 16
OK: найдено групп: 3005
Получение расписаний: 100%|█████████████████████████████| 3005/3005 [00:59<00:00, 50.51гр/s, empty=1027, failed=0] 
OK: получено расписаний: 1793
Нормализация: 100%|█████████████████████████████████████| 1793/1793 [00:00<00:00, 2504.92гр/s]
OK: занятий: 456596
DONE: сохранено в schedule.json
```

## Стек технологий

**Backend:**

- <img src="https://cdn.simpleicons.org/python/0CBFA1" width="16" /> Python 3.12
- <img src="https://cdn.simpleicons.org/json/0CBFA1" width="16" /> JSON / CSV 

**Инструменты:**

- <img src="https://cdn.simpleicons.org/httpie/0CBFA1" width="16" /> Requests + `ThreadPoolExecutor` (параллельные запросы)
- <img src="https://cdn.simpleicons.org/gnometerminal/0CBFA1" width="16" /> tqdm (прогресс-бары)

## Механика парсинга

1. **Получение структуры.** `GET /structure` возвращает дерево университета: филиал, факультет, кафедра, курс, группа. Скрипт обходит пять уровней вложенности и собирает UUID всех групп нужного филиала.
2. **Запрос расписаний.** `GET /schedules/groups/<uuid>/public` выполняется **параллельно** через `ThreadPoolExecutor`.
3. **Нормализация дат.** API отдаёт `day: 1` (понедельник) и `week: "all" | "ch" | "zn"`. Скрипт вычисляет календарную дату от `START_DATE` и номера недели по формуле `(week_number - 1) * 7 + (day_of_week - isoweekday(START_DATE))`.
4. **Чётные и нечётные недели** (в пределах `WEEKS`, по умолчанию 17):
   - `ch` — числитель, недели 1, 3, 5, … ;
   - `zn` — знаменатель, недели 2, 4, 6, … ;
   - `all` — каждую неделю.
5. **Пропуск первой недели.** Если `START_DATE` попадает на середину недели, занятия «первой недели», выпадающие раньше этой даты, отбрасываются — в итоговом JSON нет дат раньше `START_DATE`.
6. **Парсинг аудиторий.** Если массив `audiences` пуст, аудитория не назначена; иначе берётся поля `name`, `building` и `building_id` каждой аудитории (например, {`"name"`: "524", `"building"`: "A1 ГУК", `"building_id"`: 21}).

## Пример формата вывода (JSON)

```json
[
  {
      "date": "2026-12-16",
      "group_name": "ИУ5-75Б",
      "discipline": "Безопасность жизнедеятельности",
      "start_time": "08:30",
      "end_time": "10:00",
      "teachers": [
          "Борис Николаевич Рахманов"
      ],
      "audiences": [
          {
              "name": "524",
              "building": "A1 ГУК",
              "building_id": 21
          }
      ],
      "lesson_type": "lecture",
      "week_type": "all",
      "day_of_week": 3
    }
]
```
