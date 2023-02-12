import json
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

    version = sys.version_info
    if version.major != 3 or version.minor != 9:
        print('Python version 3.9 (exactly) is required')
        sys.exit()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(intents=intents, command_prefix='!')


    @bot.event
    async def on_ready():
        print("Worky is starting")
        scheduled_loop.start()

    @tasks.loop(hours=24)
    async def scheduled_loop():
        all_channels = list(bot.get_all_channels())
        af_channel = discord.utils.get(all_channels, name='platsbanken-it-spåret')

        for ad in get_ads():
            desc = ad['headline']
            link = ad['webpage_url']
            msg = f'**{desc}**\n<{link}>'
            await af_channel.send(msg)


    @bot.command(name='stopWorky')
    @commands.is_owner()
    async def stop(ctx):
        await bot.close()
        sys.exit()

    token = 'MTA2NjMxMjA4NzE2NjUyNTQ4MQ.G2ZPYd.L2LeOuEwHFxYv8c8O3DM_UwoC3U6tc61-cwFqk'
    bot.run(token=token)
