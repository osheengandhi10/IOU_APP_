from django.db import models
from django.contrib.auth.models import User
import jsonfield

# Create your models here.

def get_default_json():
    json_text = {
    "name": "",
    "owes": {

    },
    "owed_by": {
 
    },
    "balance": ""
   }
   
    return json_text



class User_IOU(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    IOU_json = jsonfield.JSONField(default = get_default_json())

    def __str__(self):
        return self.user.username

