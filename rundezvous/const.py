import datetime

from django.contrib.gis.measure import Distance

meetup_distance_threshold = Distance(m=100)
"""The maximum distance between two users where a meetup can still be created
"""

max_rundezvous_expiration = datetime.timedelta(hours=1)
"""The time after which all Rundezvouses will be assumed expired
"""
