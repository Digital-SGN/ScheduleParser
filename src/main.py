from parser import parse_schedule
from api_client import *
import datetime

print(parse_schedule(get_groups_schedule(get_group_uuids('8c1b7bb8-e690-11db-89c3-000cf1a7cbf0')), 17, datetime.date(2026, 9, 1)))