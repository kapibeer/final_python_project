from domain import WeatherRepository


class OpenWeatherAdapter(WeatherRepository):
    def get_weather(self, date, city):
        ...
