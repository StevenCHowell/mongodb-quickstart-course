import datetime
import mongoengine

class Snake(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    species = mongoengine.StringField(required=True)

    length = mongoengine.FloatField(required=True, min_value=0.01)
    name = mongoengine.StringField(required=True)
    venomous = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'snakes'
    }

