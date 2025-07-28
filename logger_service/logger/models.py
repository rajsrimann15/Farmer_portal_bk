from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
import uuid
from django_cassandra_engine.models import DjangoCassandraModel

class BaseLog(Model):
    __abstract__ = True
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.Text(required=True)
    method = columns.Text(required=True)
    route = columns.Text(required=True)
    timestamp = columns.DateTime(required=True)

class FarmerLog(BaseLog):
    __table_name__ = 'farmer_logs'

class ConsumerLog(BaseLog):
    __table_name__ = 'consumer_logs'

class TransporterLog(BaseLog):
    __table_name__ = 'transporter_logs'
