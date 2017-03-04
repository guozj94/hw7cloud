from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Messages(models.Model):
	user = models.ForeignKey(User, default=None)
	post = models.TextField(max_length=200)
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return 'user=' + str(self.id) + ',post="' + self.post + '"'

class Comments(models.Model):
	relatedmessage = models.ForeignKey(Messages, default=None, related_name='relatedmessage')
	user = models.ForeignKey(User, default=None, related_name='user')
	commentdate = models.DateTimeField(auto_now_add=True)
	comment = models.TextField(max_length=200, default=None)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	age = models.CharField(max_length=3, blank=True)
	bio = models.TextField(max_length=430, blank=True)
	picture = models.FileField(upload_to="images", default='images/defaultuserpicture.png', blank=True)
	content_type = models.CharField(max_length=50)

class Follow(models.Model):
	user = models.ForeignKey(User, default=None)
	follows = models.CharField(max_length=20)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()