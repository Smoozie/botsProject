import sys
import signal
import asyncio
import os

from dotenv import load_dotenv
import requests
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands
from datetime import date
from bs4 import BeautifulSoup


def format_days(lines, week_num):
    days = ["Måndag:", "Tisdag:", "Onsdag:", "Torsdag:", "Fredag:"]

    for idx, item in enumerate(lines):
        if item in days:
            which_day = days.index(item) + 1
            d = date.fromisocalendar(2023, week_num, which_day)
            new_item = f"**{item[:-1]} {d.day}/{d.month}:**"
            lines[idx] = new_item

    days = '\n'.join(lines)
    return days


def get_week():
    resp = requests.get("https://adelfors.nu/folkhoegskolan/veckans-matsedel/")
    soup = BeautifulSoup(resp.content, 'html.parser')
    lunch_menu_all_parts = soup.find_all(id="Header3")
    lunch_menu_flat = [item for part in lunch_menu_all_parts for item in part]
    lunch_menu = [item.text for item in lunch_menu_flat]
    lunch_menu = [item for item in lunch_menu if item != ""]
    week_line = [item for item in lunch_menu if 'vecka' in item][0]
    week_num = int(''.join(s for s in week_line if s.isdigit()))
    first_day_line = lunch_menu.index('Måndag:')
    lunch_menu = lunch_menu[first_day_line:]
    lunch_menu.insert(0, 'Detta är veckans luncher:')
    lunch_menu.insert(1, '')

    days = format_days(lunch_menu, week_num)
    return days


if __name__ == '__main__':

    load_dotenv()
    TOKEN = os.getenv('WORKY_TOKEN')

    version = sys.version_info
    if version.major != 3 or version.minor != 9:
        print('Python version 3.9 (exactly) is required')
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
    @commands.is_owner()
    async def stop(_ctx):
        await cleanup()

    bot.run(token=TOKEN)
