from django.db import models
from crum import get_current_user
from django.contrib import admin
from django.utils import timezone
import datetime
from django.contrib.auth.models import Group
# from custom_user.models import AbstractEmailUser
from storages.backends.sftpstorage import SFTPStorage

SFS = SFTPStorage()

MOOD_CHOICES = (
    ('good','😁'),
    ('ok', '🙂'),
    ('bad','😔'),
)

GENDER_CHOICES = (
    (1, 'Male'),
    (2, 'Female'),
)


class Department(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField('auth.User')

    def __str__(self):
        return self.name


class BaseModel(models.Model):
    """
    The base model which all models should inherit from.
    Provides basic fields which are usefull for all models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    repr_fields = ['id']

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
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


class Child(BaseModel):
    """
    The default User model, extended to represent customers as well as staff users.
    """
    def __str__(self) -> str:
        return self.first_name + " " + self.last_name

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
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Children"

class HangOutTheme(BaseModel):   
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class VolunteerReport(models.Model):
    description = models.CharField(max_length=200)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=get_current_user(), null=False, editable=False)
    # created_by_department = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, editable=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES, default='ok')
    # volunteer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True)
    text = models.TextField(blank = True)
    theme = models.ForeignKey(HangOutTheme, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField()
    photo = models.ImageField(upload_to='photos', storage=SFS, null=True, blank=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk:
            self.created_by = user
            # THIS PART USES CREATED DEPARTMENTS TABLE
            if Department.objects.filter(members=user):
                self.department = Department.objects.filter(members=user)[0]
            # THIS PART USES ADMIN GROUP TABLE
            # if user.groups.all()[0]:
            #     self.created_by_department = user.groups.all()[0]
        super(VolunteerReport, self).save(*args, **kwargs)

    def __str__(self):
        return self.description