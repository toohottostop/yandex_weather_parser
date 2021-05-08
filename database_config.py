from playhouse.postgres_ext import *
import functools

my_json_dumps = functools.partial(json.dumps, ensure_ascii=False)

database_proxy = DatabaseProxy()
pg_db = PostgresqlExtDatabase('weather', user='user')
database_proxy.initialize(pg_db)


class WeatherTable(Model):
    date = DateField()
    temperature = JSONField(my_json_dumps)
    weather_type = JSONField(my_json_dumps)
    pressure = JSONField(my_json_dumps)
    humidity = JSONField(my_json_dumps)
    wind = JSONField(my_json_dumps)

    class Meta:
        database = database_proxy
