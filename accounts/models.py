from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model for KostTicket application.
    Extends the default Django user model.
    """
    # Add custom fields here if needed
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
