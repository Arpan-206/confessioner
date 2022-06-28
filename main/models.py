from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

def rand_str():
    return get_random_string(length=8)

# Create your models here.
class Community(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='communities', null=True, default=None)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    join_code = models.CharField(max_length=8, default=rand_str, unique=True)

    def __str__(self):
        return self.name

class Confession(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " in " + self.community.name + " " + self.title

class User(AbstractUser):
    pass

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + str(self.confession.id)

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_on = models.DateTimeField(auto_now_add=True)
    is_mod = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username + " - " + self.community.name

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"