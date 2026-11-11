
import requests
from tqdm import tqdm


def get_group_schedule(group_id: str) -> dict | None:
    url: str = (
        f'https://lks.bmstu.ru/lks-back/api/v1/'
        f'schedules/groups/{group_id}/public'
    )

    response: requests.Response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()["data"]

        group_schedule: dict = {
            data["title"]: data["schedule"]
        }

        return group_schedule

    return None


def get_groups_schedule(group_ids: list[str]) -> dict:
    group_schedules: dict = {}

    for group_id in tqdm(
        group_ids,
        desc="Получение расписаний",
        unit="группа"
    ):
        schedule: dict | None = get_group_schedule(group_id)

        if schedule is not None:
            group_schedules.update(schedule)

    return group_schedules


def get_group_uuids(filial_uuid: str) -> list[str]:
    url: str = 'https://lks.bmstu.ru/lks-back/api/v1/structure'

    response: requests.Response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        group_ids: list[str] = []

        for filial in tqdm(
            data["data"]["children"],
            desc="Поиск филиала",
            unit="филиал"
        ):
            if filial["uuid"] == filial_uuid:

                for faculty in tqdm(
                    filial["children"],
                    desc="Обработка факультетов",
                    unit="факультет",
                    leave=False
                ):
                    for department in faculty["children"]:

                        for course in department["children"]:

                            for group in course["children"]:
                                group_ids.append(group["uuid"])

                return group_ids

    return []
print(get_groups_schedule(get_group_uuids("8c1b7bb8-e690-11db-89c3-000cf1a7cbf0")))