from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from django.apps import AppConfig
from .models import FarmerLog, ConsumerLog, TransporterLog

class LoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logger'

    def ready(self):
        from cassandra.cqlengine import connection
        connection.setup(['127.0.0.1'], "logger_keyspace")
        sync_table(FarmerLog)
        sync_table(ConsumerLog)
        sync_table(TransporterLog)
