from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.utils import timezone


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


# ----- Polls Structure ------------------------------------------------------------------------------------------------


class Poll(models.Model):
    teacher_id = models.OneToOneField('User', on_delete=models.DO_NOTHING)
    cathedra_id = models.ForeignKey('Cathedra', on_delete=models.DO_NOTHING)
    max_students = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)


class WaitList(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    STATUSES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DECLINED, "Declined")
    ]

    student_id = models.ForeignKey('User', on_delete=models.DO_NOTHING)
    poll_id = models.ForeignKey('Poll', on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(default=timezone.now)
    date_closed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, default=PENDING)

    def close(self, status):
        if status not in [self.ACCEPTED, self.DECLINED]:
            return False
        self.status = status
        self.date_closed = timezone.now()
        self.save(update_fields=["date_closed", "status"])
        return True
