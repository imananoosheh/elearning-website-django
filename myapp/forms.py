from django import forms
from myapp.models import Order, Review, Student


class SearchForm(forms.Form):
    LENGTH_CHOICES = [
        (8, '8 Weeks'),
        (10, '10 Weeks'),
        (12, '12 Weeks'),
        (14, '14 Weeks'),
    ]
    name = forms.CharField(max_length=100, required=False, label='Student Name')
    length = forms.TypedChoiceField(widget=forms.RadioSelect, choices=LENGTH_CHOICES, coerce=int, required=False,
                                    label='Preferred course duration:')
    max_price = forms.IntegerField(required=True, label='Maximum Price', min_value=0)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['courses', 'student', 'order_status']
        widgets = {'courses': forms.CheckboxSelectMultiple(), 'order_type': forms.RadioSelect}
        labels = {'student': u'Student Name', }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reviewer', 'course', 'rating', 'comments']
        widgets = {'course': forms.RadioSelect}
        labels = {'reviewer': 'please enter a valid Email', 'rating': 'Rating: An integer between 1 (worst) and 5 ('
                                                                      'best)', }


class RegisterForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name', 'email', 'level', 'address', 'province', 'registered_courses',
                  'interested_in']
        widgets = {'email': forms.EmailInput, 'level': forms.RadioSelect,
                   'registered_courses': forms.CheckboxSelectMultiple(),
                   'interested_in': forms.CheckboxSelectMultiple()}
        # , 'registered_courses': forms.CheckboxSelectMultiple(), 'interested_in': forms.CheckboxSelectMultiple()}
        # labels = [le]
