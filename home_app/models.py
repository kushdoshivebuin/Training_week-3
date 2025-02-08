from django.db import models
from datetime import datetime
from django.contrib.auth.hashers import make_password

# Create your models here.
class Contact(models.Model) :
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return 'Message from ' + self.name
    
class User(models.Model) :
    email = models.EmailField()
    username = models.CharField(primary_key=True, max_length = 50)
    password = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # Hash the password before saving it to the database
        if not self.pk:  # Check if it's a new user
            self.password = make_password(self.password)
        super().save(*args, **kwargs)