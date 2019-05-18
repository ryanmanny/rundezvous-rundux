import datetime

from django.contrib.gis.measure import Distance

# The time after which all Users will become inactive if location hasn't updated
USER_ACTIVE_TIME = datetime.timedelta(days=7)

# The time after which all Rundezvouses will be assumed expired
MAX_RUNDEZVOUS_EXPIRATION = datetime.timedelta(hours=1)
# Chat time limit
CHAT_TIME_LIMIT = datetime.timedelta(minutes=2)

# The maximum distance between two users where a meetup can still be created
MEETUP_DISTANCE_THRESHOLD = Distance(m=100)
