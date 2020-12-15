from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django import forms
from django.db import models
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200)
    length = models.IntegerField(default=12)

    def __str__(self):
        return self.name + ' [ ' + str(self.length) + ' Week ]'


class Course(models.Model):
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(50), MaxValueValidator(500)])
    for_everyone = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    num_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '[id: ' + str(self.id) + ' ] ' + self.title + '  | # of reviews: ' + str(self.num_reviews)


class Student(User):
    LVL_CHOICES = [
        ('HS', 'High School'),
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('ND', 'No Degree'),
    ]

    level = models.CharField(choices=LVL_CHOICES, max_length=2, default='HS')
    address = models.CharField(max_length=300)
    province = models.CharField(max_length=2, default='ON')
    registered_courses = models.ManyToManyField(Course, blank=True)
    interested_in = models.ManyToManyField(Topic)
    profile_picture = models.ImageField(verbose_name="Profile Picture", default="static/myapp/profilepic.png", upload_to="",
                                        blank=True)

    def __str__(self):
        return self.username + ' | ' + self.first_name + ' ' + self.last_name


class Order(models.Model):
    courses = models.ManyToManyField(Course)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ORDER_STS_CHOICES = [
        (0, 'Cancelled'),
        (1, 'Confirmed'),
        (2, 'On Hold'),
    ]
    order_status = models.IntegerField(choices=ORDER_STS_CHOICES, default=1)
    order_date = models.DateField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def total_cost(self):
        total = 0
        courses = self.student.registered_courses.all()
        for course in courses:
            total += course.price
        return total

    def total_items(self):
        total = 0
        courses = self.student.registered_courses.all()
        for course in courses:
            total += 1
        return total

    def __str__(self):
        return self.student.username + ' | ' + self.student.last_name + ', ' + self.student.first_name


class Review(models.Model):
    reviewer = models.EmailField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.reviewer + ' rated ' + self.rating + ' to ' + self.course.title

# class OrderAdmin(models.Model):
