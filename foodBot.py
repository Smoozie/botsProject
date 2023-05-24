import re
import sys
import signal
import asyncio

import requests
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands
from datetime import date
from bs4 import BeautifulSoup, ResultSet, Tag, PageElement

TOKEN = "MTA2MjgyNjY1OTE1OTQ3ODMzMw.GMmr6E.jnG0gOE3XuXCVQvnuGrXy5TXrES17VwXXGYzec"
CURRENT_YEAR = date.today().year
ADELFORS_MATSEDEL_URL = "https://adelfors.nu/folkhoegskolan/veckans-matsedel/"


def remove_colons(lines: list[str]) -> list[str]:
    days_with_colons = ["Måndag:", "Tisdag:", "Onsdag:", "Torsdag:", "Fredag:"]

    for index, line in enumerate(lines):
        if line in days_with_colons:
            day_without_colon = line[:-1]
            lines[index] = day_without_colon

    return lines


def format_days(lines: list[str], week_num: int) -> str:
    lines = remove_colons(lines)

    days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

    for index, line in enumerate(lines):
        if line in days:
            weekday = days.index(line) + 1
            date_of_day = date.fromisocalendar(CURRENT_YEAR, week_num, weekday)
            new_item = f"**{line} {date_of_day.day}/{date_of_day.month}:**"
            lines[index] = new_item

    days = '\n'.join(lines)
    return days


def merge_results(all_results: ResultSet) -> list[PageElement]:
    flat_list = []

    for result in all_results:
        assert isinstance(result, Tag)
        for item in result:
            flat_list.append(item)

    return flat_list


def get_soup() -> BeautifulSoup:
    response = requests.get(ADELFORS_MATSEDEL_URL)
    soup = BeautifulSoup(markup=response.content, features='html.parser')
    return soup


def get_week_line(soup: BeautifulSoup) -> str:
    week_line = soup.find(string=re.compile('(?i)matsedel vecka'))
    if week_line is None:
        raise ValueError

    text = week_line.text
    return text


def get_week_number(week_line: str) -> int:
    digits_list = []

    for char in week_line:
        if char.isdigit():
            digits_list.append(char)

    week_number_str = ''.join(digits_list)
    week_number = int(week_number_str)
    return week_number


def get_lunch_menu_raw(soup: BeautifulSoup) -> list[str]:
    lunch_menu_monday_elem = soup.find(string="Måndag:")
    if lunch_menu_monday_elem is None:
        lunch_menu_monday_elem = soup.find(string="Måndag")
    lunch_menu_monday_elem = lunch_menu_monday_elem.parent
    lunch_menu_whole_elem = lunch_menu_monday_elem.parent
    lunch_menu_text = [item.text for item in lunch_menu_whole_elem]
    lunch_menu = [item for item in lunch_menu_text if item != ""]
    lunch_menu = [item for item in lunch_menu if item != ":"]
    print(lunch_menu)
    return lunch_menu


def format_week_menu(week_menu: list[str]) -> list[str]:
    try:
        first_day_line = week_menu.index('Måndag:')
    except ValueError:
        first_day_line = week_menu.index('Måndag')

    week_menu = week_menu[first_day_line:]
    week_menu.insert(0, 'Detta är veckans luncher:')
    week_menu.insert(1, '')

    return week_menu


def get_weekly_lunches() -> str:
    soup = get_soup()

    lunch_menu = get_lunch_menu_raw(soup)

    week_line = get_week_line(soup)
    week_num = get_week_number(week_line)

    week_menu = format_week_menu(lunch_menu)

    days = format_days(week_menu, week_num)
    return days


if __name__ == '__main__':

    version = sys.version_info
    if version.major != 3 or version.minor != 10:
        print('Python version 3.10 (exactly) is required')
        sys.exit()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        if sys.platform == 'linux':
            bot.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(cleanup()))

    async def cleanup():
        await bot.close()
        sys.exit()

    @bot.command(name="mat")
    async def food(ctx: commands.Context):
        response = get_weekly_lunches()
        await ctx.send(response)

    @bot.command(name='stopFoody')
    async def stop(_ctx: commands.Context):
        await cleanup()

    bot.run(token=TOKEN)
