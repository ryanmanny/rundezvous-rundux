from django.contrib.gis.db import models


class LandmarkSet(models.QuerySet):
    def get_closest_to_point(self, point):
        """
        TODO: Is this good practice?
        """
        return self.distance(point).first('distance')


class LandmarkManager(models.Manager):
    pass
