from django.contrib import admin
from .models import Topic, Course, Student, Order
from django.contrib import admin, auth
import decimal

discount_amount = 0.1  # 10% Discount


def apply_discount(modeladmin, request, queryset):
    for course in queryset:
        course.price = course.price * decimal.Decimal(0.9)
        course.save()


apply_discount.short_description = "Apply 0.1 discount on selected courses"


class CourseAdmin(admin.ModelAdmin):
    fields = [('title', 'topic'), ('price', 'num_reviews', 'for_everyone')]
    list_display = ('title', 'topic', 'price')
    actions = [apply_discount]


class OrderAdmin(admin.ModelAdmin):
    fields = ['courses', ('student', 'order_status', 'order_date')]
    list_display = ('id', 'student', 'order_status', 'total_items')


class CourseInline(admin.TabularInline):
    model = Course


class TopicAdmin(admin.ModelAdmin):
    inlines = [
        CourseInline,
    ]


class StudentAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'level', 'registered_courses']
    list_display = ('first_name', 'last_name', 'level')


# Register your models here.
admin.site.register(Topic, TopicAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Order, OrderAdmin)
