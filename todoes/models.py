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
        return u";".join((self.fio,str(self.login)))
    class Meta:
        ordering = ['fio',]
class Mezuza(models.Model):
    description = models.CharField(max_length=200,blank = True, null = True)
    date_of_last_check = models.DateTimeField(blank = True, null = True)
    seller = models.ForeignKey(Person, blank = True, null = True, related_name = "seller_for_mezuza")
    worker = models.ForeignKey(Person, blank = True, null = True, related_name = "worker_for_mezuza")
    owner = models.ForeignKey('Client', blank = True, null = True, related_name = "owner_for_mezuza")
    payment = models.DecimalField(decimal_places=2, max_digits=8)
    gniza=models.BooleanField(default=False)
    def __unicode__(self):
        return u";".join((str(self.id),self.owner.fio,str(self.date_of_last_check)))
    class Meta:
        ordering = ['owner','date_of_last_check',]
class Tfilin(models.Model):
    description = models.CharField(max_length=200,blank = True, null = True)
    date_of_last_check = models.DateTimeField(blank = True, null = True)
    seller = models.ForeignKey(Person, blank = True, null = True, related_name = "seller_for_tfilin")
    worker = models.ForeignKey(Person, blank = True, null = True, related_name = "worker_for_tfilin")
    owner = models.ForeignKey('Client', blank = True, null = True, related_name = "owner_for_tfilin")
    payment = models.DecimalField(decimal_places=2, max_digits=8)
    gniza=models.BooleanField(default=False)
    def __unicode__(self):
        return u";".join((str(self.id),self.owner.fio,str(self.date_of_last_check)))
    class Meta:
        ordering = ['owner','date_of_last_check',]
class Bdikot(models.Model):
    of_what = models.TextField()
    date_of_bdika = models.DateTimeField(blank = True, null = True)
    seller = models.ForeignKey(Person, blank = True, null = True, related_name = "seller_for_bdika")
    worker = models.ForeignKey(Person, blank = True, null = True, related_name = "worker_for_bdika")
    owner = models.ForeignKey('Client', blank = True, null = True, related_name = "owner_for_bdika")
    payment = models.DecimalField(decimal_places=2, max_digits=8)
    def __unicode__(self):
        return u";".join((str(self.id),self.owner.fio,str(self.date_of_bdika)))
    class Meta:
        ordering = ['owner','date_of_bdika',]
class Claim(models.Model):
    mezuza = models.ManyToManyField('Mezuza',related_name = "for_claim", blank=True, null=True)
    tfilin = models.ManyToManyField('Tfilin',related_name = "for_claim", blank=True, null=True)
    bdikot = models.ManyToManyField('Bdikot',related_name = "for_claim", blank=True, null=True)
    discount = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    date_of_claim = models.DateTimeField()    
    get_cash = models.DecimalField(decimal_places=2, max_digits=8, blank = True, null = True)
    date_of_payment = models.DateTimeField(blank = True, null = True)
    def __unicode__(self):
        return u";".join((str(self.id),self.for_client.get().fio,str(self.date_of_claim)))
    class Meta:
        ordering = ['date_of_claim','date_of_payment',]    
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
    children_client = models.ManyToManyField('Client',related_name = "parent_client",blank = True, null = True)
    deleted = models.BooleanField(default=False)
    acl = models.TextField(default=False)
    # Заказы
    claims = models.ManyToManyField('Claim',related_name = "for_client", blank=True, null=True)
    def __unicode__(self):
        return u";".join((str(self.id),self.fio,u"\t"+self.tel))
    class Meta:
        ordering = ['fio','entering_date']

class Activity(models.Model):
    login = models.CharField(max_length=140, blank = True, null = True)
    last_page = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    def __unicode__(self):
        return u";".join((str(self.id),self.login,self.last_page,str(self.timestamp)))
    class Meta:
        ordering = ['-timestamp',]