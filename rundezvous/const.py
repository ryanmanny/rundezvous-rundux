import datetime

from django.contrib.gis.measure import Distance

# The time after which all Users will become inactive if location hasn't updated
USER_ACTIVE_TIME = datetime.timedelta(days=7)

# The time after which all Rundezvouses will be assumed expired
MAX_RUNDEZVOUS_EXPIRATION = datetime.timedelta(hours=1)
# The maximum distance between two users where a meetup can still be created
MEETUP_DISTANCE_THRESHOLD = Distance(m=800)  # About half a mile, quarter each

# Self-explanatory
MAX_CHAT_MESSAGE_LENGTH = 140
# How long users can chat before the Rundezvous Decision must be made
CHAT_TIME_LIMIT = datetime.timedelta(minutes=2)
