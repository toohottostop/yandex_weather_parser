import argparse
import os
import requests
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import cv2 as cv
from PIL import Image, ImageFont, ImageDraw
from database_config import WeatherTable
from playhouse.postgres_ext import PostgresqlExtDatabase


class WeatherMaker:
    """Class for parsing the weather of the selected city"""

    def __init__(self, city: str):
        """

        :param city: city where you want to know the weather
        """
        self.url = f'https://yandex.ru/pogoda/{city}/details?via=ms#2'
        self.weather_forecast = {}

    def parse(self):
        """

        :return: dict with 10 days weather forecast with values depending on daypart:
            - temperature
            - weather_type
            - pressure
            - humidity
            - wind_speed
        """
        response = requests.get(self.url).content
        soup = BeautifulSoup(response, 'html.parser')
        weather_table = soup.find_all('tbody', class_='weather-table__body')

        for day, table_row in zip(range(0, len(weather_table)), weather_table):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            self.weather_forecast.setdefault(date, {})
            table_cells = table_row.find_all('tr')

            for table_cell in table_cells:
                daypart = table_cell.find(class_='weather-table__daypart')
                temperature = table_cell.find_all(class_='weather-table__body-cell weather-table__'
                                                         'body-cell_type_daypart weather-table__body-cell_wrapper')
                weather_type = table_cell.find(
                    class_='weather-table__body-cell weather-table__body-cell_type_condition')
                pressure = table_cell.find(class_='weather-table__body-cell weather-table__body-cell_type_air-pressure')
                humidity = table_cell.find(class_='weather-table__body-cell weather-table__body-cell_type_humidity')
                wind = table_cell.find(class_='wind-speed')

                self.weather_forecast[date].setdefault('temperature', {})
                self.weather_forecast[date].setdefault('weather_type', {})
                self.weather_forecast[date].setdefault('pressure', {})
                self.weather_forecast[date].setdefault('humidity', {})
                self.weather_forecast[date].setdefault('wind_speed', {})

                for temp in temperature:
                    temp_values = temp.find_all(class_='temp__value')
                    self.weather_forecast[date]['temperature'].setdefault(daypart.text, [])
                    for temp_value in temp_values:
                        self.weather_forecast[date]['temperature'][daypart.text].append(
                            temp_value.text if temp_value else "N/A")

                self.weather_forecast[date]['weather_type'].setdefault(daypart.text, [])
                self.weather_forecast[date]['pressure'].setdefault(daypart.text, [])
                self.weather_forecast[date]['humidity'].setdefault(daypart.text, [])
                self.weather_forecast[date]['wind_speed'].setdefault(daypart.text, [])

                self.weather_forecast[date]['weather_type'][daypart.text].append(
                    weather_type.text if weather_type else "N/A")
                self.weather_forecast[date]['pressure'][daypart.text].append(pressure.text if pressure else "N/A")
                self.weather_forecast[date]['humidity'][daypart.text].append(humidity.text if humidity else "N/A")
                self.weather_forecast[date]['wind_speed'][daypart.text].append(wind.text if wind else "N/A")
        return self.weather_forecast


class ImageMaker:
    """Class for creating weather_card"""

    DAYPARTS = ['Morning', 'Day', 'Evening', 'Night']
    WEATHER_MEASUREMENTS = ['Temperature', 'WeatherType', 'Pressure', 'Humidity', ' Wind']
    WEATHER_TYPES_IMG = ['external_data/weather_img/cloud.jpg',
                         'external_data/weather_img/rain.jpg',
                         'external_data/weather_img/snow.jpg',
                         'external_data/weather_img/sun.jpg']
    WEATHER_TYPES_TOKENS = {
        'солнечная_погода': ['солнечно', 'ясно'],
        'дождливая_погода': ['небольшой дождь', 'дождь', 'сильный дождь', 'сильный дождь, гроза'],
        'снежная_погода': ['небольшой снег', 'снегопад', 'снег'],
        'облачная_погода': ['облачно', 'пасмурно', 'малооблачно', 'облачно с прояснениями'],
    }

    def __init__(self, weather_forecast: WeatherTable, date_weather: str):
        """

        :param weather_forecast: query to select a row from WeatherTable for a selected date
        :param date_weather: selected date
        """
        self.weather_forecast = weather_forecast
        self.date = date_weather
        self.font = ImageFont.truetype("external_data/ariblk.ttf", 20)
        self.image = cv.imread("external_data/card_template.jpg")
        self.cv_image = None

    def make_card(self):
        """
        method draw a weather card filled with data and and create a folder in which put this card
        :return: None
        """
        if self.image is None:
            print("Could not read the image.")
            return
        self.cv_image = cv.resize(self.image, (1200, 370))
        self.make_gradient()
        self.name_rows_and_columns()
        self.paste_weather_images()
        self.cv_image = cv.cvtColor(self.cv_image, cv.COLOR_BGR2RGB)
        im_pil = Image.fromarray(self.cv_image)
        draw_text = ImageDraw.Draw(im_pil)
        measures = [
            self.weather_forecast.temperature,
            self.weather_forecast.weather_type,
            self.weather_forecast.pressure,
            self.weather_forecast.humidity,
            self.weather_forecast.wind
        ]
        for x_coord, value in zip(range(200, 2500, 230), measures):
            for v, y_coord in zip(value.values(), range(120, 500, 60)):
                text = '..'.join(v)
                draw_text.text((x_coord, y_coord), text, font=self.font, fill=(210, 105, 30))
        os.makedirs(self.date, exist_ok=True)
        im_pil.save(os.path.join(self.date, f'weather_card_{self.date}.jpg'), 'JPEG')
        im_pil.show()

    def make_gradient(self):
        """
        drawing a background gradient with a color that depends on the type of weather
        :return: None
        """
        colors = [(255, 255, 255)]
        weather_type = ''.join(self.weather_forecast.weather_type['днём']).lower()
        if weather_type in self.WEATHER_TYPES_TOKENS['солнечная_погода']:
            colors = [(0 + x, 250, 250) for x in range(0, 1000, 5)]
        elif weather_type in self.WEATHER_TYPES_TOKENS['дождливая_погода']:
            colors = [(250, 20 + x, 0 + x) for x in range(0, 1000, 5)]
        elif weather_type in self.WEATHER_TYPES_TOKENS['снежная_погода']:
            colors = [(250, 240, 0 + x) for x in range(0, 1000, 5)]
        elif weather_type in self.WEATHER_TYPES_TOKENS['облачная_погода']:
            colors = [(70 + x, 70 + x, 70 + x) for x in range(0, 1000, 5)]
        for x, color in zip(range(0, 1000, 5), colors):
            cv.rectangle(self.cv_image, (0, 0 + x), (1200, 50 + x), color, -1)

    def name_rows_and_columns(self):
        """
        draw names of columns and rows in weather card
        :return: None
        """
        cv_text_color = (40, 40, 40)
        cv.putText(self.cv_image, f'Date: {self.date}', (450, 30), cv.FONT_HERSHEY_SIMPLEX, 1, cv_text_color, 4)
        for y_coord, daypart in zip(range(140, 330, 60), self.DAYPARTS):
            cv.putText(self.cv_image, daypart, (15, y_coord), cv.FONT_HERSHEY_SIMPLEX, 1, cv_text_color, 2)
        for x_coord, measurement in zip(range(160, 1100, 230), self.WEATHER_MEASUREMENTS):
            cv.putText(self.cv_image, measurement, (x_coord, 80), cv.FONT_HERSHEY_SIMPLEX, 1, cv_text_color, 2)

    def paste_weather_images(self):
        """
        insert images of weather types depending on time of day
        :return: None
        """
        weather_types = self.weather_forecast.weather_type
        for x, weather_type in zip(range(0, 281, 60), weather_types.values()):
            weather = '..'.join(weather_type)
            if weather.lower() in self.WEATHER_TYPES_TOKENS['солнечная_погода']:
                image = self.WEATHER_TYPES_IMG[3]
            elif weather.lower() in self.WEATHER_TYPES_TOKENS['дождливая_погода']:
                image = self.WEATHER_TYPES_IMG[1]
            elif weather.lower() in self.WEATHER_TYPES_TOKENS['снежная_погода']:
                image = self.WEATHER_TYPES_IMG[2]
            elif weather.lower() in self.WEATHER_TYPES_TOKENS['облачная_погода']:
                image = self.WEATHER_TYPES_IMG[0]
            else:
                break
            rsz_img2 = cv.resize(cv.imread(image), (60, 60))
            rows, cols, channels = rsz_img2.shape
            roi_img1 = self.cv_image[110 + x:170 + x, 365:365 + cols]
            roi_img2 = rsz_img2[0:rows, 0:cols]
            dst = cv.addWeighted(roi_img1, 0, roi_img2, 1, 0)
            self.cv_image[110 + x:170 + x, 365:365 + cols] = dst


class DatabaseUpdater:
    """Class for adding or getting a forecast for a selected date range"""

    def __init__(self, data_base: PostgresqlExtDatabase, weather_forecast: dict, date_start: str, date_end: str):
        """

        :param data_base: connection to data base
        :param weather_forecast: dict with forecast
        :param date_start: start date of selected interval
        :param date_end: start date of selected interval
        """
        self.data_base = data_base
        self.data_base.create_tables([WeatherTable])
        self.weather_dict = weather_forecast
        self.date_start = date_start
        self.date_end = date_end
        self.dates_search_interval = None
        self.forecasts_search_interval = None

    def save_in_database(self):
        """
        method to create or update weather forecast in database of selected interval of dates
        :return: None
        """
        self._set_search_interval()
        with self.data_base.atomic():
            for date, forecast in zip(self.dates_search_interval, self.forecasts_search_interval):
                weather, created = WeatherTable.get_or_create(
                    date=date,
                    defaults={'date': date,
                              'temperature': forecast['temperature'],
                              'weather_type': forecast['weather_type'],
                              'pressure': forecast['pressure'],
                              'humidity': forecast['humidity'],
                              'wind': forecast['wind_speed']}
                )
                if not created:
                    query = WeatherTable.update(temperature=forecast['temperature'],
                                                weather_type=forecast['weather_type'],
                                                pressure=forecast['pressure'],
                                                humidity=forecast['humidity'],
                                                wind=forecast['wind_speed']).where(WeatherTable.id == weather.id)
                    query.execute()

    def get_from_database(self):
        """
        method to get weather forecast from database of selected interval of dates
        :return: WeatherTable object
        """
        query = WeatherTable.select().where(WeatherTable.date.between(self.date_start, self.date_end))
        return query

    def _set_search_interval(self):
        """
        helper method for selecting values from a dictionary for a selected date range
        :return: None
        """
        dates = list(self.weather_dict.keys())
        forecasts = list(self.weather_dict.values())
        if self.date_end == self.date_start:
            start_write = dates.index(self.date_start)
            self.dates_search_interval = [dates[start_write]]
            self.forecasts_search_interval = [forecasts[start_write]]
        else:
            start_write = dates.index(self.date_start)
            end_write = dates.index(self.date_end) + 1
            self.dates_search_interval = dates[start_write:end_write]
            self.forecasts_search_interval = forecasts[start_write:end_write]


class Manager:
    """Manager class to operate with WeatherMaker, ImageMaker and DatabaseUpdater classes"""

    @staticmethod
    def draw_card(args: argparse.Namespace):
        """
        method to draw a weather card for the selected date
        :param args: passed arguments
        :return: None
        """
        query = WeatherTable.get(WeatherTable.date == args.date)
        image_maker = ImageMaker(weather_forecast=query, date_weather=args.date)
        image_maker.make_card()

    @staticmethod
    def add_to_database(args: argparse.Namespace):
        """
        method to parse weather and add selected interval of dates
        :param args: passed arguments
        :return: None
        """
        weather = WeatherMaker(city=args.city)
        db_updater = DatabaseUpdater(data_base=args.db, weather_forecast=weather.parse(),
                                     date_start=args.date_start,
                                     date_end=args.date_end)
        db_updater.save_in_database()

    @staticmethod
    def get_from_database(args: argparse.Namespace):
        """
        method to get weather forecast of selected interval of dates and print it in console
        :param args: passed arguments
        :return: None
        """
        db_updater = DatabaseUpdater(data_base=args.db, weather_forecast={},
                                     date_start=args.date_start,
                                     date_end=args.date_end)

        for data in db_updater.get_from_database():
            print(f'Дата: {data.date}\n'
                  f'Температура: {data.temperature}\n'
                  f'Тип погоды: {data.weather_type}\n'
                  f'Давление: {data.pressure}\n'
                  f'Влажность: {data.humidity}\n'
                  f'Скорость ветра: {data.wind}\n', type(args))
