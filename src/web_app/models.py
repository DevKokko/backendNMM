from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#IMPORTANT don't forget to register the models in the admin.py


class User_Info_Manager(models.Manager):
    def create_user_info(self, user):
        user_info = self.create(user=user)
        return user_info

class User_Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    elo = models.IntegerField(default=2000)
    verification_token = models.CharField(max_length=32,default='')
    is_banned = models.BooleanField(default=False)
    is_verified_account = models.BooleanField(default=False)

    objects = User_Info_Manager()


class Reports_Manager(models.Manager):
    def create_reports(self, user):
        reports = self.create(user=user)
        return reports

class Reports(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING, unique=False, related_name="reporter")
    reported = models.ForeignKey(User, on_delete=models.DO_NOTHING, unique=False, related_name="reported")

    class Meta:
        unique_together = (("reporter", "reported"),)
        
    objects = Reports_Manager()


class Friends_Manager(models.Manager):
    def create_reports(self, user):
        friends = self.create(user=user)
        return friends


class Friends(models.Model):
    #user_1_id < user_2_id, stored in ascending order
    user_1 = models.ForeignKey(User, on_delete=models.DO_NOTHING, unique=False, related_name="user_1")
    user_2 = models.ForeignKey(User, on_delete=models.DO_NOTHING, unique=False, related_name="user_2")
    
    class Meta:
        unique_together = (("user_1", "user_2"),)
    
    objects = Reports_Manager()