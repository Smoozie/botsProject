import sys
import signal
import asyncio

import requests
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands
from datetime import date
from bs4 import BeautifulSoup

TOKEN = "MTA2MjgyNjY1OTE1OTQ3ODMzMw.GMmr6E.jnG0gOE3XuXCVQvnuGrXy5TXrES17VwXXGYzec"
CURRENT_YEAR = date.today().year


def remove_colons(lines):
    days_with_colons = ["Måndag:", "Tisdag:", "Onsdag:", "Torsdag:", "Fredag:"]

    for index, line in enumerate(lines):
        if line in days_with_colons:
            day_without_colon = line[:-1]
            lines[index] = day_without_colon

    return lines


def format_days(lines, week_num):
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


def flatten(list_of_lists):
    flat_list = []

    for lst in list_of_lists:
        for item in lst:
            flat_list.append(item)

    return flat_list


def get_week():
    resp = requests.get("https://adelfors.nu/folkhoegskolan/veckans-matsedel/")
    soup = BeautifulSoup(resp.content, 'html.parser')
    lunch_menu_all_parts = soup.find_all(id="Header3")
    lunch_menu_flat = flatten(lunch_menu_all_parts)
    lunch_menu = [item.text for item in lunch_menu_flat]
    lunch_menu = [item for item in lunch_menu if item != ""]
    week_line = [item for item in lunch_menu if 'vecka' in item][0]
    week_num = int(''.join(s for s in week_line if s.isdigit()))

    try:
        first_day_line = lunch_menu.index('Måndag:')
    except ValueError:
        first_day_line = lunch_menu.index('Måndag')

    lunch_menu = lunch_menu[first_day_line:]
    lunch_menu.insert(0, 'Detta är veckans luncher:')
    lunch_menu.insert(1, '')

    days = format_days(lunch_menu, week_num)
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
        print(f"{bot.user} is now online")
        if sys.platform == 'linux':
            bot.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(cleanup()))

    async def cleanup():
        await bot.close()
        sys.exit()

    @bot.command(name="mat")
    async def food(ctx: commands.Context):
        response = get_week()
        await ctx.send(response)

    @bot.command(name='stopFoody')
    async def stop(_ctx):
        await cleanup()

    bot.run(token=TOKEN)
