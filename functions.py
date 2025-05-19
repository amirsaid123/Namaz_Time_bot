import aiohttp
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bs4 import BeautifulSoup


async def make_keyboard_button(btns_name: list, adjust: list):
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[KeyboardButton(text=name) for name in btns_name])
    rkb.adjust(*adjust)
    return rkb.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def make_inline_button(btns_name: list, adjust: list):
    inline = InlineKeyboardBuilder()
    inline.add(
        *[
            InlineKeyboardButton(
                text=name,
                callback_data=f"{name.split()[0].lower()}"
            )
            for name in btns_name
        ]
    )

    inline.adjust(*adjust)
    return inline.as_markup()


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def normalize_text(text):
    return (
        text.lower()
        .replace("g‘", "g")  # Replace Uzbek-specific apostrophe
        .replace("ғ", "g")  # Replace Cyrillic "ғ" if needed
        .replace("’", "")  # Unicode apostrophe
        .replace("‘", "")  # Left single quotation mark
        .replace("`", "")  # Grave accent
        .replace("ʼ", "")
        .replace("'", "")  # Modifier letter apostrophe
    )


async def get_districts(city_name):
    print(f"Fetching districts for {city_name}")
    city = await normalize_text(city_name)
    print(f"Modified city name:{city}")  # Debugging
    url = f"https://www.namozvaqti.uz/viloyat/{city}"
    html = await fetch_url(url)
    soup = BeautifulSoup(html, "lxml")

    districts = []
    cities = soup.find_all("div", class_="col-xl-4 col-xs-12 py-1")

    for city in cities:
        districts.append(city.text.strip())

    return districts


async def get_time_districts(district_name):
    print(f"Fetching time districts for {district_name}")
    district = await normalize_text(district_name)
    print(f"Modified district name {district}")  # Debugging
    url = f"https://www.namozvaqti.uz/shahar/{district}"
    html = await fetch_url(url)

    if not html:
        return None

    soup = BeautifulSoup(html, "lxml")
    names = soup.find_all("h2", class_="nam")
    times = soup.find_all("p", class_="time")
    day_element = soup.find("h5", class_="vil")

    if not names or not times or not day_element:
        return None

    day = day_element.text.split('-')[0].strip()
    namazs = [{"Day": day}]

    for i in range(6):
        d = {
            "Name": names[i].text.strip(),
            "Time": times[i].text.strip()
        }
        namazs.append(d)

    return namazs
