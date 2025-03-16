from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order, JewelryOrder


from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('user', 'User'), ('staff', 'Staff')], required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    # เพิ่มส่วน __init__() ที่คุณให้มา
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        # ปรับแต่งฟิลด์ในฟอร์ม
        self.fields['username'].help_text = ""  # ลบข้อความช่วยเหลือ
        self.fields['password2'].help_text = ""
        self.fields['username'].widget.attrs.update({
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'
        })



class UploadImageForm(forms.Form):
    image = forms.ImageField()


class JewelryOrderForm(forms.ModelForm):
    class Meta:
        model = JewelryOrder
        fields = ['details', 'quantity', 'image']
