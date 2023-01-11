from django.db import models
from django.contrib.auth import models as auth_models
# from django.shortcuts import reverse
from django.core.exceptions import ValidationError

# tips (see docs: https://docs.djangoproject.com/en/4.0/topics/db/models/):
#   - Model.objects : all modelObjects methods
#       - create : create object and auto save to db
#       - get : returns object (raise error if not found or found more then one)
#       - filter : returns objects
#   - modelObject.save()  : saves model object to db


# ----- University Structure -------------------------------------------------------------------------------------------


class Specialization(models.Model):
    code = models.IntegerField(max_length=3, db_index=True, unique=True)
    name = models.CharField(max_length=150)
    descr = models.CharField(max_length=150)


class Faculty(models.Model):
    name = models.CharField(max_length=150)
    abbr = models.CharField(max_length=16)


class Cathedra(models.Model):
    faculty_id = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    abbr = models.CharField(max_length=16)


class Group(models.Model):
    cathedra_id = models.ForeignKey('Cathedra', on_delete=models.CASCADE)
    specialization_id = models.ForeignKey('Specialization', on_delete=models.CASCADE)
    name = models.CharField(max_length=32)


# ----- Users Structure ------------------------------------------------------------------------------------------------


class User(auth_models.AbstractUser):

    # roles ------------------
    STUDENT = 1
    TEACHER = 2
    ROLES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher")
    ]
    # ------------------------

    email = models.EmailField()
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    patronymic = models.CharField(max_length=32, null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLES, default=STUDENT)

    def get_full_name(self):
        """ returns full name: `LastName FirstName *Patronymic` """
        full_name = "%s %s" % (self.last_name, self.first_name)
        if self.patronymic is not None:
            full_name += " %s" % self.patronymic
        return full_name.strip()


# roles


class BaseRole(models.Model):

    ROLE_ID = None
    user_id = models.OneToOneField('User', on_delete=models.CASCADE)

    class Meta:
        abstract = True

    # todo: validate role


class Student(BaseRole):
    ROLE_ID = User.STUDENT

    group_id = models.ForeignKey('Group', on_delete=models.SET_NULL)
    teacher_id = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)

    # todo: validate teacher (can't be myself or not teacher)


class Teacher(BaseRole):
    ROLE_ID = User.TEACHER

    position = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=512, blank=True, null=True)

