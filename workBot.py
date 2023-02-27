import asyncio
import json
import signal
import sys

import requests
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import tasks, commands
from datetime import datetime
from datetime import timedelta

BASE_URL = 'https://jobstream.api.jobtechdev.se'
STREAM_URL = f"{BASE_URL}/stream"

JONKOPINGS_LAN = 'MtbE_xWT_eMi'

YRKESGRUPP_2511 = 'UXKZ_3zZ_ipB'
YRKESGRUPP_2512 = 'DJh5_yyF_hEM'
YRKESGRUPP_2513 = 'Q5DF_juj_8do'
YRKESGRUPP_2514 = 'D9SL_mtn_vGM'
YRKESGRUPP_2515 = 'cBBa_ngH_fCx'
YRKESGRUPP_2516 = 'BAeH_eg8_T2d'
YRKESGRUPP_2519 = 'UxT1_tPF_Kbg'
YRKESGRUPP_251 = [YRKESGRUPP_2511, YRKESGRUPP_2512, YRKESGRUPP_2513, YRKESGRUPP_2514,
                  YRKESGRUPP_2515, YRKESGRUPP_2516, YRKESGRUPP_2519]
YRKESGRUPP_3511 = '13md_uyV_BNG'
YRKESGRUPP_3512 = 'hmaC_cfi_UKg'
YRKESGRUPP_3513 = 'MYAz_x9m_2LJ'
YRKESGRUPP_3514 = 'VCpu_5EN_bBt'
YRKESGRUPP_3515 = 'Fv7d_YhP_YmS'
YRKESGRUPP_351 = [YRKESGRUPP_3511, YRKESGRUPP_3512, YRKESGRUPP_3513, YRKESGRUPP_3514, YRKESGRUPP_3515]

YRKEN = YRKESGRUPP_251
YRKEN.extend(YRKESGRUPP_351)

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


def matching_date(ad, date):
    pub_date = ad['publication_date']
    pub_date = datetime.strptime(pub_date, DATE_FORMAT)
    return pub_date.date() == date.date()


def filter_ads(ads_list, date):
    filtered = [ad for ad in ads_list if not ad['removed']]
    filtered = [ad for ad in filtered if matching_date(ad, date)]
    return filtered


def fetch_stream(timestamp: datetime):
    td = timedelta(days=1)
    prev_day = timestamp - td
    params = {
        'date': prev_day.strftime(DATE_FORMAT),
        'updated-before-date': timestamp.strftime(DATE_FORMAT),
        'location-concept-id': JONKOPINGS_LAN,
        'occupation-concept-id': YRKEN
    }
    response = requests.get(STREAM_URL, params=params)
    return response.content


def get_ads():
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0)
    td = timedelta(days=1)
    start_of_yesterday = start_of_day - td
    stream = fetch_stream(start_of_day)
    all_ads = json.loads(stream)
    relevant_ads = filter_ads(all_ads, start_of_yesterday)
    return relevant_ads


if __name__ == '__main__':

    TOKEN = "MTA2NjMxMjA4NzE2NjUyNTQ4MQ.GA8xRn.aC29C0-mmuAwdp11EDDKf3KHwtqSy5yqVW4mRU"

    version = sys.version_info
    if version.major != 3 or version.minor != 10:
        print('Python version 3.10 (exactly) is required')
        sys.exit()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(intents=intents, command_prefix='!')

    async def cleanup():
        await bot.close()
        sys.exit()

    @bot.event
    async def on_ready():
        print("Worky is starting")
        if sys.platform == 'linux':
            bot.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(cleanup()))
        scheduled_loop.start()

    @tasks.loop(hours=24)
    async def scheduled_loop():
        af_channel_id = 1065372918344843274
        af_channel = bot.get_channel(af_channel_id)

        all_ads = get_ads()

        for ad in all_ads:
            desc = ad['headline']
            link = ad['webpage_url']
            msg = f'**{desc}**\n<{link}>'
            await af_channel.send(msg)

    @bot.command(name='stopWorky')
    @commands.is_owner()
    async def stop(_ctx):
        await cleanup()

    bot.run(token=TOKEN)
