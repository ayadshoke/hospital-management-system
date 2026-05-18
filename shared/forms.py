from django import forms
from departs.models import Departments,Doctors,Appointments,Patients,Area,Days
from accounts.models import CustomUser,Profile


class DepartForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = '__all__'
        exclude = ['slug',]


class DocForm(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = '__all__'
        exclude = ['slug','part']

class AppointForm(forms.ModelForm):
    class Meta:
        model = Appointments
        fields = ('patient','doctor','detect')

class PatientForm(forms.ModelForm):
    """ اول طريقة """
    area = forms.ModelChoiceField(queryset=Area.objects.all(),empty_label=('اختر المنطقة'))
    """ الطريقة الثانية """
    # areas = Area.objects.all()
    # choices = [(area.name,area.code) for area in areas]
    # area = forms.ChoiceField(choices=choices)
    class Meta:
        model = Patients
        fields = '__all__'
        exclude = ['slug']
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)

class DayForm(forms.ModelForm):
    class Meta:
        model = Days
        fields = '__all__'


class CustForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields =('first_name','last_name','email','phone','image','address')

class ProForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('age','jop')


