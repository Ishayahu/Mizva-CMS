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
        '%d.%m.%Y %H:%M:%S',     # '10/25/2006 14:30:59'
        '%Y.%m.%d %H:%M:%S',     # '2010/01/26 14:30:59'
        '%d/%m/%y %H:%M:%S',     # '10/25/06 14:30:59'
        '%d/%m/%y %H:%M',        # '10/25/06 14:30'
        '%d/%m/%y',       )
class NewClientForm(forms.Form):
    fio = forms.CharField(max_length=140, label='ФИО клиента')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    #manager = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Менеджер')
    #priority = forms.ChoiceField(widget=forms.RadioSelect,choices = PRIORITY_CHOICES, label='Приоритет')
    #category = forms.ModelChoiceField(queryset  = Categories.objects.all(), label='Категория')
    #entering_date = forms.DateTimeField(label='Дата внесения',input_formats=inp_f)
    #exiting_date = forms.DateTimeField(label='Дата выхода из системы',input_formats=inp_f)
    mail = forms.EmailField(label = 'Мыло',required=False)
    tel = forms.CharField(label='Телефон', max_length=10, min_length=10,required=False)
    #number = forms.IntegerField(label='Количество заказанных мезузот',required=False)
    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
    #payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
    #get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
class EditClientForm(forms.Form):
    fio = forms.CharField(max_length=140, label='ФИО клиента')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    #manager = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Менеджер')
    #priority = forms.ChoiceField(widget=forms.RadioSelect,choices = PRIORITY_CHOICES, label='Приоритет')
    #category = forms.ModelChoiceField(queryset  = Categories.objects.all(), label='Категория')
    entering_date = forms.DateTimeField(label='Дата внесения',input_formats=inp_f)
    exiting_date = forms.DateTimeField(label='Дата выхода из системы',input_formats=inp_f,required=False)
    mail = forms.EmailField(label = 'Мыло',required=False)
    tel = forms.CharField(label='Телефон', max_length=10, min_length=10,required=False)
#class NewClaimForm(forms.Form):
#    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    number = forms.IntegerField(label='Количество заказанных мезузот')
#    payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
#    get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
#class EditClaimForm(forms.Form):
#    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    number = forms.IntegerField(label='Количество заказанных мезузот')
#    date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    date_of_installation = forms.DateTimeField(label='Дата установки мезузы',input_formats=inp_f,required=False)
#    seller = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Продавец')
#    worker = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Установщик',required=False)
#    payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
#    get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
#    date_of_payment = forms.DateTimeField(label='Дата последнего внесения денег',input_formats=inp_f)
 
class ClientSearchForm(forms.Form):
    name = forms.CharField(max_length=140, label='Строка для поиска')
class NoteToClientAddForm(forms.Form):
    #def __init__(self, *args, **kwargs):
    #    self.defaults = kwargs.pop('defaults','')
    #    self.exclude = kwargs.pop('exclude','')
    #    super(NoteToTicketAddForm, self).__init__(*args, **kwargs)
    #    self.fields['workers'].queryset = Person.objects.exclude(fio__in = [person.fio for person in self.exclude ])
    #    self.fields['workers'].initial = Person.objects.filter(fio__in = self.defaults)

    note = forms.CharField(widget=forms.Textarea, label='Комментарий',required=False )
    #workers = forms.ModelMultipleChoiceField(queryset  = Person.objects.all(), label='Кого ещё уведомить о комментарии?',required=False,)
class UserCreationFormMY(UserCreationForm):
    fio = forms.CharField(label='ФИО')
    mail = forms.EmailField(label = 'Мыло')
    tel = forms.CharField(label='Телефон', max_length=10, min_length=10)
    
    
    
class NewClientForm_ENG(forms.Form):
    fio = forms.CharField(max_length=140, label='Name of client')
    description = forms.CharField(widget=forms.Textarea, label='Description')
    #manager = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Менеджер')
    #priority = forms.ChoiceField(widget=forms.RadioSelect,choices = PRIORITY_CHOICES, label='Приоритет')
    #category = forms.ModelChoiceField(queryset  = Categories.objects.all(), label='Категория')
    #entering_date = forms.DateTimeField(label='Дата внесения',input_formats=inp_f)
    #exiting_date = forms.DateTimeField(label='Дата выхода из системы',input_formats=inp_f)
    mail = forms.EmailField(label = 'E-mail',required=False)
    tel = forms.CharField(label='Phone', max_length=10, min_length=10,required=False)
    #number = forms.IntegerField(label='Количество заказанных мезузот',required=False)
    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
    #payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
    #get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
class EditClientForm_ENG(forms.Form):
    fio = forms.CharField(max_length=140, label='Name of client')
    description = forms.CharField(widget=forms.Textarea, label='Description')
    #manager = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Менеджер')
    #priority = forms.ChoiceField(widget=forms.RadioSelect,choices = PRIORITY_CHOICES, label='Приоритет')
    #category = forms.ModelChoiceField(queryset  = Categories.objects.all(), label='Категория')
    entering_date = forms.DateTimeField(label='Entering date',input_formats=inp_f)
    exiting_date = forms.DateTimeField(label='Exititng date',input_formats=inp_f,required=False)
    mail = forms.EmailField(label = 'E-mail',required=False)
    tel = forms.CharField(label='Phone', max_length=10, min_length=10,required=False)
#class NewClaimForm(forms.Form):
#    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    number = forms.IntegerField(label='Количество заказанных мезузот')
#    payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
#    get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
#class EditClaimForm(forms.Form):
#    #date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    number = forms.IntegerField(label='Количество заказанных мезузот')
#    date_of_claim = forms.DateTimeField(label='Дата создания заявки',input_formats=inp_f)
#    date_of_installation = forms.DateTimeField(label='Дата установки мезузы',input_formats=inp_f,required=False)
#    seller = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Продавец')
#    worker = forms.ModelChoiceField(queryset  = Person.objects.all(), label='Установщик',required=False)
#    payment = forms.DecimalField(decimal_places=2, max_digits=8,label='Итоговая стоимость',required=False)
#    get_cash = forms.DecimalField(decimal_places=2, max_digits=8,label='Внесено денег',required=False)
#    date_of_payment = forms.DateTimeField(label='Дата последнего внесения денег',input_formats=inp_f)
 
class ClientSearchForm_ENG(forms.Form):
    name = forms.CharField(max_length=140, label='String to search')
class NoteToClientAddForm_ENG(forms.Form):
    #def __init__(self, *args, **kwargs):
    #    self.defaults = kwargs.pop('defaults','')
    #    self.exclude = kwargs.pop('exclude','')
    #    super(NoteToTicketAddForm, self).__init__(*args, **kwargs)
    #    self.fields['workers'].queryset = Person.objects.exclude(fio__in = [person.fio for person in self.exclude ])
    #    self.fields['workers'].initial = Person.objects.filter(fio__in = self.defaults)

    note = forms.CharField(widget=forms.Textarea, label='Note',required=False )
    #workers = forms.ModelMultipleChoiceField(queryset  = Person.objects.all(), label='Кого ещё уведомить о комментарии?',required=False,)
class UserCreationFormMY_ENG(UserCreationForm):
    fio = forms.CharField(label='Name')
    mail = forms.EmailField(label = 'E-mail')
    tel = forms.CharField(label='Phone', max_length=10, min_length=10)