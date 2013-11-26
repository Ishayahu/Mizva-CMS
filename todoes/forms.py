# -*- coding:utf-8 -*-
# coding=<utf8>
from django import forms
from todoes.models import Note, File, Person, Client, Mezuza, Categories
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin import widgets

PRIORITY_CHOICES = (
        ('1','Лазар/Борода/Мотя'),
        ('2','Если не сделать сейчас - огребём проблем потом'),
        ('3','Всё остальное'),
        ('4','В ближайшем будущем'),
        ('5','Когда время будет')
    )

inp_f=( '%d-%m-%Y %H:%M:%S',     # '2006-10-25 14:30:59'
        '%d-%m-%Y %H:%M',        # '2006-10-25 14:30'
        '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30'
        '%d-%m-%Y',              # '25-10-2025'
        '%Y-%m-%d',              # '2006-10-25'
        '%d/%m/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
        '%d/%m/%Y %H:%M',        # '10/25/2006 14:30'
        '%d/%m/%Y',              # '10/25/2006'
        '%Y/%m/%d',              # '2010/12/31'
        '%d.%m.%Y %H:%M:%S',     # '10/25/2006 14:30:59'
        '%Y.%m.%d %H:%M:%S',     # '2010/01/26 14:30:59'
        '%d/%m/%y %H:%M:%S',     # '10/25/06 14:30:59'
        '%d/%m/%y %H:%M',        # '10/25/06 14:30'
        '%d/%m/%y',       )
class NewClientForm(forms.Form):
    fio = forms.CharField(max_length=140, label='ФИО клиента')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    mail = forms.EmailField(label = 'Мыло',required=False)
    tel = forms.CharField(label='Телефон', min_length=10,required=False)
    dr = forms.DateTimeField(label='День рождения',input_formats=inp_f,required=False)
    spouse_fio = forms.CharField(max_length=140, label='ФИО супруга(и)',required=False)
    spouse_tel = forms.CharField(label='Телефон супруга(и)', max_length=10, min_length=10,required=False)
    spouse_mail = forms.EmailField(label = 'Мыло супруга(и)',required=False)
    spouse_dr = forms.DateTimeField(label='День рождения супруга(и)',input_formats=inp_f,required=False)
    home_tel = forms.CharField(label='Домашний телефон', max_length=10, min_length=10,required=False)
    address = forms.CharField(widget=forms.Textarea, label='Адресс',required=False)
    file  = forms.FileField(label="Прикрепить аватар", required=False)
    def clean_tel(self):
        data = self.cleaned_data
        raw_tel =data['tel']
        tel = ''
        if raw_tel[:2]=="+7":
            tel = raw_tel[2:]
        if raw_tel[:2]=="7":
            tel = raw_tel[1:]
        tel = tel.replace(" ","")
        if len(tel)>10:
            raise forms.ValidationError('Номер телефона слишком длинный') 
        return tel
class EditClientForm(forms.Form):
    fio = forms.CharField(max_length=140, label='ФИО клиента')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    entering_date = forms.DateTimeField(label='Дата внесения',input_formats=inp_f)
    exiting_date = forms.DateTimeField(label='Дата выхода из системы',input_formats=inp_f,required=False)
    mail = forms.EmailField(label = 'Мыло',required=False)
    tel = forms.CharField(label='Телефон', min_length=10,required=False)
    dr = forms.DateTimeField(label='День рождения',input_formats=inp_f,required=False)
    spouse_fio = forms.CharField(max_length=140, label='ФИО супруга(и)',required=False)
    spouse_tel = forms.CharField(label='Телефон супруга(и)', max_length=10, min_length=10,required=False)
    spouse_mail = forms.EmailField(label = 'Мыло супруга(и)',required=False)
    spouse_dr = forms.DateTimeField(label='День рождения супруга(и)',input_formats=inp_f,required=False)
    home_tel = forms.CharField(label='Домашний телефон', max_length=10, min_length=10,required=False)
    address = forms.CharField(widget=forms.Textarea, label='Адрес',required=False)
    file  = forms.FileField(label="Прикрепить аватар", required=False)
    def clean_tel(self):
        data = self.cleaned_data
        raw_tel =data['tel']
        tel = ''
        if raw_tel[:2]=="+7":
            tel = raw_tel[2:]
        if raw_tel[:2]=="7":
            tel = raw_tel[1:]
        tel = tel.replace(" ","")
        if len(tel)>10:
            raise forms.ValidationError('Номер телефона слишком длинный') 
        return tel
class ClientSearchForm(forms.Form):
    name = forms.CharField(max_length=140, label='Строка для поиска',required=False)
    date = forms.DateTimeField(label='Дата покупки',input_formats=inp_f,required=False)
    mezuza = forms.BooleanField(label='Поиск по мезузам', required=False)
    tfilin = forms.BooleanField(label='Поиск по тфилинам', required=False)
class NoteToClientAddForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea, label='Комментарий',required=False )
class UserCreationFormMY(UserCreationForm):
    error_css_class = 'user_creation_error'
    required_css_class = 'new_worker_tr'
    fio = forms.CharField(label='ФИО')
    mail = forms.EmailField(label = 'Мыло')
    tel = forms.CharField(label='Телефон', max_length=10, min_length=10)
    
    
    
class NewClientForm_ENG(forms.Form):
    fio = forms.CharField(max_length=140, label='Name of client')
    description = forms.CharField(widget=forms.Textarea, label='Description')
    mail = forms.EmailField(label = 'E-mail',required=False)
    tel = forms.CharField(label='Phone', max_length=10, min_length=10,required=False)
    dr = forms.DateTimeField(label='Birthday',input_formats=inp_f,required=False)
    spouse_fio = forms.CharField(max_length=140, label='Spouse`s name',required=False)
    spouse_tel = forms.CharField(label='Spouse`s phone', max_length=10, min_length=10,required=False)
    spouse_mail = forms.EmailField(label = 'Spouse`s e-mail',required=False)
    spouse_dr = forms.DateTimeField(label='Spouse`s Birthday',input_formats=inp_f,required=False)
    home_tel = forms.CharField(label='Home phone number', max_length=10, min_length=10,required=False)
    address = forms.CharField(widget=forms.Textarea, label='Address',required=False)    
    file  = forms.FileField(label="Add avatar", required=False)
    def clean_tel(self):
        data = self.cleaned_data
        raw_tel =data['tel']
        tel = ''
        if raw_tel[:2]=="+7":
            tel = raw_tel[2:]
        if raw_tel[:2]=="7":
            tel = raw_tel[1:]
        tel = tel.replace(" ","")
        if len(tel)>10:
            raise forms.ValidationError('Telephone number is too long') 
        return tel
class EditClientForm_ENG(forms.Form):
    fio = forms.CharField(max_length=140, label='Name of client')
    description = forms.CharField(widget=forms.Textarea, label='Description')
    entering_date = forms.DateTimeField(label='Entering date',input_formats=inp_f)
    exiting_date = forms.DateTimeField(label='Exititng date',input_formats=inp_f,required=False)
    mail = forms.EmailField(label = 'E-mail',required=False)
    tel = forms.CharField(label='Phone', max_length=10, min_length=10,required=False)
    dr = forms.DateTimeField(label='Birthday',input_formats=inp_f,required=False)
    spouse_fio = forms.CharField(max_length=140, label='Spouse`s name',required=False)
    spouse_tel = forms.CharField(label='Spouse`s phone', max_length=10, min_length=10,required=False)
    spouse_mail = forms.EmailField(label = 'Spouse`s e-mail',required=False)
    spouse_dr = forms.DateTimeField(label='Spouse`s Birthday',input_formats=inp_f,required=False)
    home_tel = forms.CharField(label='Home phone number', max_length=10, min_length=10,required=False)
    address = forms.CharField(widget=forms.Textarea, label='Address',required=False) 
    file  = forms.FileField(label="Add avatar", required=False)
    def clean_tel(self):
        data = self.cleaned_data
        raw_tel =data['tel']
        tel = ''
        if raw_tel[:2]=="+7":
            tel = raw_tel[2:]
        if raw_tel[:2]=="7":
            tel = raw_tel[1:]
        tel = tel.replace(" ","")
        if len(tel)>10:
            raise forms.ValidationError('Telephone number is too long') 
        return tel
class ClientSearchForm_ENG(forms.Form):
    name = forms.CharField(max_length=140, label='String to search')
    date = forms.DateTimeField(label='Date of claim',input_formats=inp_f,required=False)
    mezuza = forms.BooleanField(label='Search for mezuzot', required=False)
    tfilin = forms.BooleanField(label='Search for tfillins', required=False)
class NoteToClientAddForm_ENG(forms.Form):
    note = forms.CharField(widget=forms.Textarea, label='Note',required=False )
class UserCreationFormMY_ENG(UserCreationForm):
    fio = forms.CharField(label='Name')
    mail = forms.EmailField(label = 'E-mail')
    tel = forms.CharField(label='Phone', max_length=10, min_length=10)