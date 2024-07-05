import asyncio
import json
from aiohttp import ClientSession, web


async def get_weather(city):
    """Функция принимает название города в качестве аргумента,
    делает запрос к API OpenWeatherMap и возвращает информацию
    о текущей погоде в этом городе."""
    async with ClientSession() as session:
        url = f'http://api.openweathermap.org/data/2.5/weather'
        params = {'q': city, 'APPID': '3s5dd97g0sss81152rtv8r81fd543sbf67'}

        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            try:
                return weather_json["weather"][0]["main"]
            except KeyError:
                return 'Данные недоступны'


async def get_translation(text, source, target):
    """Функция принимает текст, язык источника и язык перевода,
    делает запрос к API LibreTranslate и возвращает переведенный текст."""
    async with ClientSession() as session:
        url = 'https://libretranslate.de/translate'

        data = {'q': text, 'source': source, 'target': target, 'format': 'text'}

        async with session.post(url, json=data) as response:
            translate_json = await response.json()

            try:
                return translate_json['translatedText']
            except KeyError:
                return text


async def process_request(request):
    """Функция-обработчик, получает запрос с параметром 'city' в URL,
    переводит название города с русского на английский,
    получает информацию о погоде и переводит ее с английского на русский,
    а затем возвращает JSON-ответ с городом и погодой."""
    city_ru = request.rel_url.query['city']
    city_en = await get_translation(city_ru, 'ru', 'en')

    weather_en = await get_weather(city_en)
    weather_ru = await get_translation(weather_en, 'en', 'ru')

    result = {'city': city_ru, 'weather': weather_ru}

    return web.Response(text=json.dumps(result, ensure_ascii=False))


async def main():
    """Функция создает веб-приложение на базе библиотеки aiohttp,
    добавляет маршрут для обработки запросов к '/weather',
    запускает сервер и ждет запросов."""
    app = web.Application()
    app.add_routes([web.get('/weather', process_request)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())