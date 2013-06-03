# -*- coding:utf-8 -*-
# coding=<utf8>

from django.db import models

# Create your models here.
class Categories(models.Model):
    name = models.TextField()
    def __unicode__(self):
        # return u';'.join((str(self.id),self.name))
        return self.name
    
class Note(models.Model):
    timestamp = models.DateTimeField()
    note = models.TextField()
    author = models.ForeignKey('Person',blank = True, null = True)
    children_note = models.ManyToManyField('Note',related_name = "parent_note",blank = True, null = True)
    def __unicode__(self):
        return self.note

class File(models.Model):
    timestamp = models.DateTimeField()
    file_name = models.CharField(max_length=140)
    file = models.FileField(upload_to='task_files') # add separation by tasks
    description = models.TextField()
    class Meta:
        ordering = ['timestamp']
    def __unicode__(self):
        return str(self.id)+" "+self.file_name
    @models.permalink
    def get_absolute_url(self):
        return ('todoes.views.test_task',('one_time',self.id),{})
        # return ('food.views.restaurant_details', (), {'restaurant_id': [str(self.id)]})
        # return ('food.views.restaurant_details', (str(self.id),), {})

class Person(models.Model):
    fio = models.CharField(max_length=140)
    tel = models.CharField(max_length=10)
    mail = models.EmailField(blank = True, null = True)
    raiting = models.CharField(max_length=30, blank = True, null = True)
    login = models.CharField(max_length=140, blank = True, null = True)
    def __unicode__(self):
        return ";".join((self.fio,str(self.login)))
    class Meta:
        ordering = ['fio',]
class Mezuza(models.Model):
    number = models.IntegerField()
    date_of_claim = models.DateTimeField()
    date_of_installation = models.DateTimeField()
    worker = models.ForeignKey(Person)
    payment = models.DecimalField(decimal_places=2, max_digits=8)
    get_cash = models.DecimalField(decimal_places=2, max_digits=8)
    date_of_payment = models.DateTimeField()
    def __unicode__(self):
        return ";".join((self.fio,str(self.login)))
    class Meta:
        ordering = ['fio',]
class Client(models.Model):
    fio = models.CharField(max_length=140,blank = True, null = True)
    tel = models.CharField(max_length=10,blank = True, null = True)
    mail = models.EmailField(blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    priority = models.PositiveSmallIntegerField(blank = True, null = True)
    category = models.ForeignKey(Categories,blank = True, null = True)
    entering_date = models.DateTimeField(blank = True, null = True)
    exiting_date = models.DateTimeField(blank = True, null = True)
    when_to_reminder = models.DateTimeField(blank = True, null = True)
    manager = models.ForeignKey(Person,blank = True, null = True)
    note = models.ManyToManyField(Note, related_name = "for_client",blank = True, null = True)
    file = models.ManyToManyField(File, related_name = "for_client", blank = True, null = True)
    confirmed = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(blank = True, null = True)
    children_client = models.ManyToManyField('Task',related_name = "parent_client",blank = True, null = True)
    deleted = models.BooleanField(default=False)
    acl = models.TextField(default=False)
    # Мивцы
    mezuza = models.ManyToManyField('Mezuza',related_name = "for_client", blank=True, null=True)
    def __unicode__(self):
        return u";".join((str(self.id),self.name,"\t"+self.worker.fio))
    class Meta:
        ordering = ['priority','due_date']

class Activity(models.Model):
    login = models.CharField(max_length=140, blank = True, null = True)
    last_page = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    def __unicode__(self):
        return u";".join((str(self.id),self.login,self.last_page,str(self.timestamp)))
    class Meta:
        ordering = ['-timestamp',]