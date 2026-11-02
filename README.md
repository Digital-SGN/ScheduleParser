# ScheduleParser: Ядро данных расписания

**Скрипт для сбора, нормализации и сохранения расписания МГТУ им. Баумана (LKS) в удобный файл.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/JSON-format-000000?style=flat-square&logo=json&logoColor=white" />
  <img src="https://img.shields.io/badge/LKS-API-0CBFA1?style=flat-square" />
</p>

---

## О проекте

Сырые данные из API LKS сложны для обработки: в них нет прямых календарных дат, есть сложная структура факультетов, а информация об аудиториях приходит в специфичном формате. 

Скрипт решает три задачи:
- <img src="https://cdn.simpleicons.org/python/0CBFA1" width="16" /> **Сбор данных:** забирает расписание через API LKS по UUID группы.
- <img src="https://cdn.simpleicons.org/json/0CBFA1" width="16" /> **Нормализация:** превращает сырые дни недели в реальные календарные даты, а UUID аудиторий — в понятные номера (например, "501").
- <img src="https://cdn.simpleicons.org/databricks/0CBFA1" width="16" /> **Сохранение:** выгружает готовые данные в локальный файл (JSON/CSV). Расписание меняется редко (раз в семестр), поэтому база данных избыточна.

>  **Этот скрипт — фундамент для будущих проектов:**
> - <img src="https://cdn.simpleicons.org/googlemaps/0CBFA1" width="16" /> Поиск свободных аудиторий (где можно посидеть или провести мероприятие).
> - <img src="https://cdn.simpleicons.org/gnometerminal/0CBFA1" width="16" /> Калькулятор нагрузки (поиск оптимального времени, чтобы пришло больше людей).

---

## Стек технологий

**Backend:**
- <img src="https://cdn.simpleicons.org/python/0CBFA1" width="16" /> Python 3.12
- <img src="https://cdn.simpleicons.org/json/0CBFA1" width="16" /> JSON / CSV (выходной формат)

**Инструменты:**
- <img src="https://cdn.simpleicons.org/requests/0CBFA1" width="16" /> Requests (для запросов к LKS)
- <img src="https://cdn.simpleicons.org/docker/0CBFA1" width="16" /> Docker (опционально)

---

## Архитектура

```mermaid
flowchart LR
    LKS["API LKS МГТУ"]
    Parser["Parser (Python)"]
    File[("JSON/CSV Файл")]

    LKS -->|"GET /schedules"| Parser
    Parser -->|"Нормализация и парсинг"| File
    
    classDef api fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#334155;
    classDef parser fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef db fill:#e0e7ff,stroke:#6366f1,stroke-width:2px,color:#312e81;
    
    class LKS api;
    class Parser parser;
    class File db;
```

---

## Механика парсинга

1. **Получение структуры:** скрипт скачивает дерево факультетов и групп, чтобы найти UUID нужных групп.
2. **Запрос расписания:** идёт запрос на `schedules/groups/<uuid>/private`.
3. **Нормализация дат:** API отдаёт `day: 1` (понедельник) и `week: "all"`. Скрипт сам подставляет календарную дату, опираясь на `semesterStarts` и `weekNumber` из эндпоинта `/current`.
4. **Обработка нечетных/четных недель:** скрипт корректно раскладывает расписание для "числителя" и "знаменателя".
5. **Парсинг аудиторий:** если массив `audiences` пуст — значит, аудитория не назначена. Если есть — извлекаем номер и корпус.

---

## Пример формата вывода (JSON)

На выходе получаем чистый JSON-файл:

```json
[
  {
    "group_name": "СГН3-35Б",
    "date": "2026-10-19",
    "start_time": "10:15",
    "end_time": "11:50",
    "discipline": "Информатика",
    "lesson_type": "lab",
    "teachers": ["Хузин А.Ф."],
    "audience": "501",
    "week_type": "all" 
  }
]
```

---

## Открытые вопросы

1. **API LKS:** нужно проверить, отдаёт ли сервер информацию о занятости аудиторий в целом (или только для конкретной группы).
2. **Авторизация:** LKS может требовать токен или cookie для доступа к API. Нужно проверить через Postman/Insomnia.
