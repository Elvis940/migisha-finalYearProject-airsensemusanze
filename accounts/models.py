from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('city_planner', 'City Planner'),
        ('research', 'Research'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('denied', 'Denied'),
    )
    
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name="customuser_set",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name="customuser_set",
        related_query_name="customuser",
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ✅ Add this below the CustomUser class
class SensorData(models.Model):
    aqi = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AQI: {self.aqi}, Temp: {self.temperature}°C, Humidity: {self.humidity}%"
