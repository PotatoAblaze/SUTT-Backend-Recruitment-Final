from django.db import models
from django.conf import settings
from django.urls import reverse
from django.dispatch import receiver

from datetime import date

# Create your models here.

from django.contrib.auth.models import AbstractUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, password=None):
        
        user = self.model()

        user.set_password(password)
        user.save(using=self._db)
        return user

class MyUser(AbstractUser):
    user_name = models.CharField(name="Name", max_length=50, null=True)
    bits_id = models.CharField(name="BITS_ID", max_length=14, null=True, unique=True)
    psrn_number = models.BigIntegerField(name="PSRN_No", null=True)
    hostel = models.CharField(name="Hostel", max_length=50, null=True)
    mess = models.CharField(name="Mess", max_length=50, null=True)
    
    USERNAME_FIELD = 'username'
    
    def __str__(self) -> str:
        return(self.Name or '')


class Menu(models.Model):
    
    menu_json = models.JSONField("menu", null=True)
    
    def __str__(self) -> str:
        return "MENU"


class Dish(models.Model):
    dish_name = models.CharField(name='dish', max_length=40)
    
    def __str__(self):
        return(self.dish)
    

class Rating(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    rating_date = models.DateField(name='date', default=date.today)
    
    value = models.IntegerField(name="rating")
    
    def __str__(self):
        return(f"{self.dish.dish} by {self.user.username}: {self.rating} points")
    
    
class Complaint(models.Model):
    complaint_id = models.IntegerField(unique=True, primary_key=True)
    student = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateField(name='date', auto_now_add=True)
    title = models.TextField(name='title', max_length=256)
    description = models.TextField(name='description', max_length=3000)
    image = models.ImageField(name='image', upload_to='complaints/', null=True)
    
    def __str__(self):
        desc = f"{self.complaint_id}: {self.title} by {self.student.username}"
        return desc



class AttendanceRecord(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    date = models.DateField(name='date', auto_now_add=True)
    meal_type = models.IntegerField(name='meal_type')
    
    def __str__(self) -> str:
        desc = f"{self.user.username} on {self.date}"
        return desc
    
    
    



