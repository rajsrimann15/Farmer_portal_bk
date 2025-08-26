from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
import atexit



class SelfPriceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'self_price'

    def ready(self):
        # Prevent double execution during runserver autoreload
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .tasks import create_weekly_pricing_sessions,deactivate_all_sessions

        scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

        # Schedule the tasks
        scheduler.add_job(
            create_weekly_pricing_sessions,
            trigger=CronTrigger(day_of_week='fri', hour=16, minute=0),
            id='weekly_pricing_sessions',
            replace_existing=True
        )

        
        scheduler.add_job(
            deactivate_all_sessions,
            trigger=CronTrigger(day_of_week='sun', hour=14, minute=0),
            id='deactivate_sessions',
            replace_existing=True
        )

        scheduler.start()
        print("APScheduler started")

        atexit.register(lambda: scheduler.shutdown())
