from apscheduler.schedulers.asyncio import AsyncIOScheduler
import atexit
import requests
from json import JSONDecodeError
from tzlocal import get_localzone
import datetime
import os, time

from definitions import Roles
roles = Roles()
scheduler = AsyncIOScheduler()

n_time_h = int(os.getenv("EVENT_NOTIFICATION_TIME_HOUR"))
n_time_m = int(os.getenv("EVENT_NOTIFICATION_TIME_MIN"))
offset = int(os.getenv("TZ_OFFSET"))

async def scheule_builder():
    time.tzset()
    roles.log.warning('starting scheduler')
    roles.log.warning(get_localzone())
    roles.log.warning(datetime.datetime.now())
    scheduler.add_job(func=get_events, trigger="cron",
                    hour=n_time_h, minute=n_time_m)
    scheduler.start()
    roles.log.warning('job added')
    atexit.register(lambda: scheduler.shutdown())

async def get_events():
    try:
        roles.log.warning('looking for events')
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
        response = requests.get(f'{roles.BASE_URL}/api/calendar/getevents', headers=headers, verify=roles.VERIFY_SSL)
        events = response.json()
        roles.log.warning(events)
        roles.log.warning(datetime.datetime.now())
        announcement = f'Events in the next 24 hours: `(all times are {get_localzone()})`\n'
        if events != []:
            for event in events:
                roles.log.warning(event)
                roles.log.warning(time.timezone)
                date = datetime.datetime.strptime(event['date'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=offset)
                announcement += f'{event["name"]} `in` {event["game"]} `at` {date}\n'
                if event['note'] != '':
                    announcement += f'`{event["note"]}`\n'
                announcement += '\n'
            await roles.announcements.send(announcement)
            return
        roles.it_channel.send('no events today')
    except JSONDecodeError:
        await roles.it_channel.send('failed to import events, did not receve valid object from api')