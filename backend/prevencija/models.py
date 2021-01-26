import datetime
import random
import string
import uuid
from collections import Counter
from enum import Enum
from typing import Dict, List, Tuple

import cloudinary
from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import date

class BaseModel(models.Model):
    """
    The base model which all models should inherit from.
    Provides basic fields which are usefull for all models.
    """

    id = models.UUIDField(primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    repr_fields = ['id']

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Generic way of handling `__repr__` representations by using `self.repr_fields`.
        """

        field_values = [
            f'`{getattr(self, field)}`'
            for field in self.repr_fields
        ]
        class_name = self.__class__.__name__

        return '{class_name}({field_values})'.format(
            class_name=class_name,
            field_values=', '.join(field_values),
        )

GENDER_MALE = 0
GENDER_FEMALE = 1
GENDER_CHOICES = [(GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female')]
class User(AbstractEmailUser, BaseModel):
    """
    The default User model, extended to represent customers as well as staff users.
    """
    def __str__(self) -> str:
        return self.first_name + " " + self.last_name + " (" + self.email + ")"

    first_name = models.CharField(
        max_length=50,
    )

    last_name = models.CharField(
        max_length=50,
    )

    jmbg = models.CharField(
        max_length=13,
        unique=True,
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)



class Child(BaseModel):   
    def __str__(self) -> str:
        return self.first_name + " " + self.last_name + " (" + self.jmbg + ")"

    first_name = models.CharField(
        max_length=50,
    )

    last_name = models.CharField(
        max_length=50,
    )

    jmbg = models.CharField(
        max_length=13,
        unique=True,
    )

    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Children"


class VolunteerReport(BaseModel):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date_completed = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    completed = models.BooleanField()
    report = models.TextField(max_length=1000, null=True, blank=True,)