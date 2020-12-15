from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Import necessary classes
from datetime import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from .models import Topic, Course, Student, Order
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .forms import SearchForm, OrderForm, ReviewForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.

def index(request):
    if request.session.get('last_login'):
        last_login = request.session['last_login']
    else:
        last_login = "Your last login was more than one hour ago"
    top_list = Topic.objects.all().order_by('id')[:10]
    return render(request, 'myapp/index.html', {'top_list': top_list, 'last_login': last_login})


def about(request):
    if request.session.get('about_visits'):
        about_visits_number = request.session['about_visits']
        about_visits_number += 1
        request.session['about_visits'] = about_visits_number
        request.session.set_expiry(300)
    else:
        request.session['about_visits'] = 1
        request.session.set_expiry(300)

    about_visits_number = request.session['about_visits']
    about_message = 'This is an E-learning Website! Search our Topics to find all available Courses.'
    return render(request, 'myapp/about.html', {'about_message': about_message, 'visits_number': about_visits_number})


def detail(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    related_courses = Course.objects.filter(topic=topic_id)
    return render(request, 'myapp/detail.html',
                  {'topic_id': topic_id, 'topic': topic, 'related_courses': related_courses})


def findcourses(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        length = form.cleaned_data['length']
        max_price = form.cleaned_data['max_price']
        if length:
            topics = Topic.objects.filter(length=length)
        else:
            topics = Topic.objects.all()
        courselist = []
        for top in topics:
            for course in list(top.courses.all()):

                if course.price <= max_price:
                    courselist.append(str(course.title))

        return render(request, 'myapp/results.html',
                      {'courselist': courselist, 'name': name, 'length': length, 'max_price': max_price})
    else:
        return HttpResponse('Invalid data')
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save(commit=False)
            student = order.student
            status = order.order_status
            order.save()
            if status == 1:
                for c in courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html', {'courses': courses, 'order': order})
        else:
            return render(request, 'myapp/place_order.html', {'form': form})

    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form': form})


def review_view(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=True)
            rating = form.cleaned_data['rating']
            course = form.cleaned_data['course']
            review.save()

            if 1 <= rating <= 5:
                course.num_reviews += 1
                course.save()
                top_list = Topic.objects.all().order_by('id')
                error_message = 'Thank you for reviewing the course: ' + str(course.title) + '!'
                return render(request, 'myapp/review.html', {'form': form, 'error_message': error_message})
            else:
                form = ReviewForm()
                error_message = 'You must enter a rating between 1 and 5!'
                return render(request, 'myapp/review.html', {'form': form, 'error_message': error_message})
    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        current_login = datetime.now()
        username = request.POST['username']
        password = request.POST['password']
        next = request.POST['next']
        print("NEXT VALUE: " + str(request.POST['next']) + str(type(request.POST['next'])))
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                # response.set_cookie('last_login', str(current_login), max_age=6000)
                request.session['last_login'] = str(current_login)
                request.session.set_expiry(6000)
                # return HttpResponse(reverse('myapp:index'))
                # print(get_redirect_field_name())
                if next == 'None':
                    print("redirecting to home: " + str(reverse('myapp:index')))
                    print(str(request.POST['next']))
                    return HttpResponseRedirect(reverse('myapp:index'))
                else:
                    print("redirecting to next: " + str(next))
                    # return redirect(request.GET.get('/myapp/', next))
                    print("it reaches here ______")
                    return redirect(next)
                # return redirect(request.GET.get('next'))
                # return render(request, 'myapp/index.html')

            else:
                return render(request, 'myapp/login.html', {'error_message': 'Your account is disabled.'})
        else:
            return render(request, 'myapp/login.html', {'error_message': 'Invalid login details.'})
    else:
        next = request.GET.get('next')
        request.session['next'] = request.GET.get('next', '/')
        print(next)
        return render(request, 'myapp/login.html', {'next': str(next)})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:index'))


@login_required(login_url='/myapp/login/')
def myaccount(request):
    if request.method == 'GET':
        username = request.user.username
        print(username)
        try:
            student = Student.objects.get(username=username)
            first_name = student.first_name
            last_name = student.last_name
            interested_in = student.interested_in
            registered_courses = student.registered_courses
            profile_picture_url = student.profile_picture.url
            print(profile_picture_url)
            topic_list = []
            for topic in interested_in.all():
                topic_list.append(topic)
            course_list = []
            for course in registered_courses.all():
                course_list.append(course)
            return render(request, 'myapp/myaccount.html',
                          {'first_name': first_name, 'last_name': last_name, 'topic_list': topic_list,
                           'course_list': course_list, 'profile_picture_url': profile_picture_url})
        except Student.DoesNotExist:
            return render(request, 'myapp/register.html', {'error_message': 'You are not a registered student!'})
    else:
        return render(request, 'myapp/login.html', {'error_message': 'You are not logged in!'})


@login_required(login_url='/myapp/login/')
def myorders(request):
    if request.method == 'GET':
        username = request.user.username
        print(username)
        try:
            student = Student.objects.get(username=username)
            print(student)
            first_name = student.first_name
            last_name = student.last_name
            student_fullname = {
                'first_name': str(student.first_name),
                'last_name': str(student.last_name)
            }

            order_list = []
            orders = Order.objects.filter(student=student)
            print(orders)
            for order in orders:
                record = [order.id, order.order_date, order.order_status, order.total_items()]
                order_list.append(record)

            print(order_list)
            return render(request, 'myapp/myorders.html', {'student': student_fullname, 'order_list': order_list})

        except Student.DoesNotExist:
            return render(request, 'myapp/register.html', {'error_message': 'You are not a registered student!'})
    else:
        return render(request, 'myapp/login.html', {'error_message': 'You are not logged in!'})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            level = form.cleaned_data['level']
            address = form.cleaned_data['address']
            province = form.cleaned_data['province']
            registered_courses = form.cleaned_data['registered_courses']
            interested_in = form.cleaned_data['interested_in']
            student = form.save(commit=False)
            # student = order.student
            # status = order.order_status
            student.save()
            # if status == 1:
            #     for c in courses.all():
            #         student.registered_courses.add(c)
            topic_list = []
            for topic in interested_in.all():
                topic_list.append(topic)
            course_list = []
            for course in registered_courses.all():
                course_list.append(course)
            error_message = 'New student (username: ' + str(username) + ' ) is registered!'
            return render(request, 'myapp/myaccount.html',
                          {'error_message': error_message, 'first_name': first_name, 'last_name': last_name,
                           'topic_list': topic_list,
                           'course_list': course_list})
        else:
            return render(request, 'myapp/register.html', {'form': form})

    else:
        form = RegisterForm()
        return render(request, 'myapp/register.html', {'form': form})