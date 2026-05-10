from django.db import models

class PrivacyChoices(models.TextChoices):
    EVERYONE = 'EVERYONE', 'everyone' 
    ONLYCONTACTS = "ONLY_CONTACTS" , "only_contacts" 
    NOONE = "NO_ONE" , "no_one" 
   