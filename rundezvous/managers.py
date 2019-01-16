from django.db import models


class SiteUserSet(models.QuerySet):
    def add_close_users(self):
        """I think this will have to be a crummy approximation for now
        """
        pass


class SiteUserManager(models.Manager):
    pass
