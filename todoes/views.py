# -*- coding:utf-8 -*-
# coding=<utf8>

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
import datetime
from todoes.models import Note, File, Person, Client, Categories, Activity, Mezuza, Claim, Tfilin, Bdikot
from todoes.forms import NewClientForm, EditClientForm, ClientSearchForm, NoteToClientAddForm, UserCreationFormMY
from todoes.forms import NewClientForm_ENG, EditClientForm_ENG, ClientSearchForm_ENG, NoteToClientAddForm_ENG, UserCreationFormMY_ENG
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from itertools import chain

from djlib.cron_utils import decronize, crontab_to_russian, generate_next_reminder
from djlib.text_utils import htmlize
from djlib.acl_utils import acl
from djlib.user_tracking import set_last_activity_model, get_last_activities
from djlib.mail_utils import send_email_alternative
from djlib.error_utils import FioError

from user_settings.settings import server_ip, admins, admins_mail
from user_settings.settings import todoes_url_not_to_track as url_not_to_track
from user_settings.settings import todoes_url_one_record as url_one_record

from todoes.utils import build_note_tree, note_with_indent

#task_types = {'one_time':Task,'regular':RegularTask}
task_addr = {'one_time':'one_time','regular':'regular'}
languages={'ru':'RUS/',
            'eng':'ENG/'}
forms_RUS = {'NewClientForm':NewClientForm, 'EditClientForm':EditClientForm, 'ClientSearchForm':ClientSearchForm, 'NoteToClientAddForm':NoteToClientAddForm, 'UserCreationFormMY':UserCreationFormMY}
forms_ENG = {'NewClientForm':NewClientForm_ENG, 'EditClientForm':EditClientForm_ENG, 'ClientSearchForm':ClientSearchForm_ENG, 'NoteToClientAddForm':NoteToClientAddForm_ENG, 'UserCreationFormMY':UserCreationFormMY_ENG}
l_forms = {'ru':forms_RUS,
           'eng':forms_ENG,
    }

def save_file(files,id):
    instanse = File(file=files['file'],
                    timestamp=datetime.datetime.now(),
                    file_name = 'avatar '+str(id),
                    description = 'avatar for '+str(id),)
    instanse.save()
    return instanse
def set_last_activity(login,url):
    set_last_activity_model(login,url,url_not_to_track,url_one_record)

@login_required
def new_client(request):
    lang=select_language(request)
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError
    method = request.method
    if request.method == 'POST':
        form = NewClientForm(request.POST)
        if form.is_valid():
            # проверка - есть ли файл надо добавить


            data = form.cleaned_data
            c=Client(fio=data['fio'], 
                    tel = data['tel'],
                    mail = data['mail'],
                    description = data['description'],
                    entering_date = datetime.datetime.now(),
                    dr = data['dr'],
                    spouse_fio = data['spouse_fio'],
                    spouse_tel = data['spouse_tel'],
                    spouse_mail = data['spouse_mail'],
                    spouse_dr = data['spouse_dr'],
                    home_tel = data['home_tel'],
                    address = data['address'])
            c.save()
            if request.FILES:
                c.file.add(save_file(request.FILES,c.id))
            c.save()
            # отправляем уведомление исполнителю по мылу
            #send_email_alternative(u"Новая задача: "+t.name,t.description+u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/one_time/"+str(t.id),[data['workers'].mail,data['clients'].mail],fio)
            #set_last_activity(user,request.path)
            return HttpResponseRedirect("/client_claims/"+str(c.id))
    else:
        form = l_forms[lang]['NewClientForm']()
    #set_last_activity(user,request.path)
    # return render_to_response(languages[lang]+'new_ticket.html', {'form':form, 'method':method,'path':request.path.replace("/","+")},RequestContext(request))
	return render_to_response(languages[lang]+'edit_ticket.html', {'worker':fio,'form':form, 'method':method,'path':request.path.replace("/","+")},RequestContext(request))

@login_required
def client_claims(request,client_id):
    lang=select_language(request)
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    try:
        client_full = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        request.session['my_error'] = u'Нет такого клиента. Номер %s!' % client_id
        return HttpResponseRedirect("/")
    method = request.method
    if request.method == 'POST':
        number_of_mezuzot = request.POST['number_of_mezuzot']
        number_of_tfilins = request.POST['number_of_tfilins']
        c = Claim(discount = request.POST['discount'],
                    date_of_claim = datetime.datetime.now(),
                    get_cash = request.POST['get_cash'],
                    )
        if c.get_cash:
            c.date_of_payment = datetime.datetime.now()
        c.save()
        c.for_client.add(client_full)
        c.save()
        # Проходимся по мезузам
        for i in range(1,int(number_of_mezuzot)+1):
            if 'mezuza_desc_'+str(i) in request.POST:
                try:
                    worker = Person.objects.get(id=request.POST['mezuza_worker_'+str(i)])
                except Person.DoesNotExist:
                    worker = False
                m=Mezuza(description = request.POST['mezuza_desc_'+str(i)],
                        date_of_last_check = datetime.datetime.now(),
                        worker = worker,
                        seller = fio,
                        owner = client_full,
                        payment = request.POST['mezuza_payment_'+str(i)],
                        gniza=False,
                        )
                m.save()
                c.mezuza.add(m)
        for i in range(1,int(number_of_tfilins)+1):
            if 'tfilin_desc_'+str(i) in request.POST:
                try:
                    worker = Person.objects.get(id=request.POST['tfilin_worker_'+str(i)])
                except Person.DoesNotExist:
                    worker = False
                t=Tfilin(description = request.POST['tfilin_desc_'+str(i)],
                        date_of_last_check = datetime.datetime.now(),
                        worker = worker,
                        seller = fio,
                        owner = client_full,
                        payment = request.POST['tfilin_payment_'+str(i)],
                        gniza=False,
                        )
                t.save()
                c.tfilin.add(t)
        if "bdikot_text" in request.POST and request.POST['bdikot_text']!=u'':
            try:
                worker = Person.objects.get(id=request.POST['bdikot_worker'])
            except Person.DoesNotExist:
                worker = False
            b_txt = request.POST['bdikot_text']
            b_txt=b_txt.split(';')[:-1]
            of_what=''
            payment=0
            for item in b_txt:
                w,p = item.split(',')
                of_what=w+";"
                payment+=int(p)
            b=Bdikot(of_what = of_what,
                    date_of_bdika = datetime.datetime.now(),
                    seller = fio,
                    worker = worker,
                    owner = client_full,
                    payment = payment
                    )
            b.save()
            c.bdikot.add(b)
            c.save()
            item_type = {'mezuza':Mezuza,
                        'tfilin':Tfilin}
            for item in b.of_what.split(';')[:-1]:
                w,n=item.split('_')
                i = item_type[w].objects.get(id=n)
                i.date_of_last_check=datetime.datetime.now().replace(year=datetime.datetime.now().year + 1)
                i.save()
        # отправляем уведомление исполнителю по мылу
        #send_email_alternative(u"Новая повторяющаяся задача: "+t.name,t.description+u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/regular/"+str(t.id),[data['workers'].mail,data['clients'].mail],fio)
        #set_last_activity(user,request.path)
        return HttpResponseRedirect(request.get_full_path())
    else:
        #form = NewClaimForm()
    #set_last_activity(user,request.path)
    # Рисуем историю заказов
        claims=''
        try:
            claims=Claim.objects.filter(for_client=client_full).order_by('-date_of_claim')
        except Claim.DoesNotExist:
            pass
        for c in claims:
            c.description=u''
            full_pay=0
            got_pay=0
            ms=Mezuza.objects.filter(for_claim=c)
            c.description+=u'%s мезуз\n' % len(ms)
            for m in ms:
                full_pay+=m.payment
                #got_pay+=m.get_cash            
            ts=Tfilin.objects.filter(for_claim=c)
            c.description+=u'%s тфилинов\n' % len(ts)
            for t in ts:
                full_pay+=t.payment
                #got_pay+=t.get_cash
            try:
                b=Bdikot.objects.get(for_claim=c)
                c.description+=u'%s проверок мезуз/тфилинов\n' % (len(b.of_what.split(';'))-1)
                full_pay+=b.payment
                #got_pay+=t.get_cash
            except Bdikot.DoesNotExist:
                pass
            c.rest_cash = int(full_pay-c.get_cash-c.discount)
            c.payment = full_pay-c.discount
        # Для нового счёта: работники, имеющиеся активные мезузы и тфилины
        workers=Person.objects.all()
        mezuzas = Mezuza.objects.filter(owner=client_full).filter(gniza=False)
        tfilins = Tfilin.objects.filter(owner=client_full).filter(gniza=False)
        can_bdika=False
        if mezuzas or tfilins:
            can_bdika=True
    return render_to_response(languages[lang]+'client_claims.html', {'can_bdika':can_bdika,'client':client_full,'worker':fio,'workers':workers,'mezuzas':mezuzas,'tfilins':tfilins, 'method':method,'claims':claims,'path':request.path.replace("/","+").replace("/","+")},RequestContext(request))
@login_required
def edit_claim(request,claim_id):
    lang=select_language(request)
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    method = request.method
    user = request.user.username
    try:
        manager = Person.objects.get(login=user)
    except Person.DoesNotExist:
        manager = FioError()
    try:
        c=Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        request.session['my_error'] = u'Нет такого заказа. Номер %s!' % claim_id
        return HttpResponseRedirect("/")
    full_pay=0
    got_pay=0
    ms = c.mezuza.all()
    ts = c.tfilin.all()
    b=False
    if c.bdikot.count():
        b = c.bdikot.get()
        full_pay+=b.payment
    for m in ms:
        full_pay+=m.payment
        m.price = str(m.payment).replace(',','.')
    for t in ts:
        full_pay+=t.payment
        t.price = str(t.payment).replace(',','.')
    c.rest_cash = full_pay-c.get_cash-c.discount
    c.payment = full_pay-c.discount
    c.full_pay=full_pay
    
    workers=Person.objects.all()
    
    if request.method == 'POST':
        client_full = c.for_client.get()
        number_of_mezuzot = request.POST['number_of_mezuzot']
        number_of_tfilins = request.POST['number_of_tfilins']
        # c = Claim(discount = request.POST['discount'],
                    # date_of_claim = datetime.datetime.now(),
                    # get_cash = request.POST['get_cash'],
                    # )
        if int(float(request.POST['get_cash'])) != int(float(c.get_cash)):
            c.date_of_payment = datetime.datetime.now()
            c.get_cash = int(float(request.POST['get_cash']))
        if request.POST['discount'] != 0:
            c.discount = int(float(request.POST['discount']))
        c.save()
        # c.for_client.add(client_full)
        # c.save()
        # Проходимся по мезузам
        for i in range(1,int(number_of_mezuzot)+1):
            if 'mezuza_desc_'+str(i) in request.POST:
                try:
                    worker = Person.objects.get(id=request.POST['mezuza_worker_'+str(i)])
                except Person.DoesNotExist:
                    worker = False
                m=Mezuza(description = request.POST['mezuza_desc_'+str(i)],
                        date_of_last_check = datetime.datetime.now(),
                        worker = worker,
                        seller = fio,
                        owner = client_full,
                        payment = request.POST['mezuza_payment_'+str(i)],
                        gniza=False,
                        )
                m.save()
                c.mezuza.add(m)
        for i in range(1,int(number_of_tfilins)+1):
            if 'tfilin_desc_'+str(i) in request.POST:
                try:
                    worker = Person.objects.get(id=request.POST['tfilin_worker_'+str(i)])
                except Person.DoesNotExist:
                    worker = False
                t=Tfilin(description = request.POST['tfilin_desc_'+str(i)],
                        date_of_last_check = datetime.datetime.now(),
                        worker = worker,
                        seller = fio,
                        owner = client_full,
                        payment = request.POST['tfilin_payment_'+str(i)],
                        gniza=False,
                        )
                t.save()
                c.tfilin.add(t)
        if "bdikot_text" in request.POST and request.POST['bdikot_text']!=u'':
            try:
                worker = Person.objects.get(id=request.POST['bdikot_worker'])
            except Person.DoesNotExist:
                worker = False
            b_txt = request.POST['bdikot_text']
            b_txt=b_txt.split(';')[:-1]
            of_what=''
            payment=0
            for item in b_txt:
                w,p = item.split(',')
                of_what=w+";"
                payment+=int(p)
            b=Bdikot(of_what = of_what,
                    date_of_bdika = datetime.datetime.now(),
                    seller = fio,
                    worker = worker,
                    owner = client_full,
                    payment = payment
                    )
            b.save()
            c.bdikot.add(b)
            c.save()
            item_type = {'mezuza':Mezuza,
                        'tfilin':Tfilin}
            for item in b.of_what.split(';')[:-1]:
                w,n=item.split('_')
                i = item_type[w].objects.get(id=n)
                i.date_of_last_check=datetime.datetime.now().replace(year=datetime.datetime.now().year + 1)
                i.save()
        return HttpResponseRedirect("/client_claims/"+str(client_full.id))
    c.get_cash = str(c.get_cash).replace(',','.')
    c.discount = str(c.discount).replace(',','.')
    return render_to_response(languages[lang]+'edit_payment.html', {'worker':fio,'claim':c,'bdikot':b,'mezuzot':ms,'tfilins':ts,'workers':workers,'path':request.path.replace("/","+").replace("/","+")},RequestContext(request))
@login_required
def delete_asset(request,asset_type,id):
    lang=select_language(request)
    item_type = {'mezuza':Mezuza,
                'tfilin':Tfilin}
    try:
        item = item_type[asset_type].objects.get(id=id)
    except item_type[asset_type].DoesNotExist:
        pass
    item.delete()
    return render_to_response(languages[lang]+'OK.html', {'path':request.path.replace("/","+")},RequestContext(request))
@login_required
def edit_asset(request,asset_type,id):
    lang=select_language(request)
    item_type = {'mezuza':Mezuza,
                'tfilin':Tfilin}
    item_name = {'mezuza':'Мезуза',
                'tfilin':'Тфилин'}
    try:
        item = item_type[asset_type].objects.get(id=id)
    except item_type[asset_type].DoesNotExist:
        pass
    item.name=item_name[asset_type]
    item.price = str(item.payment).replace(',','.')
    item.item_type = asset_type
    item.tr_name = asset_type+'_'+id
    workers=Person.objects.all()
    return render_to_response(languages[lang]+'edit_asset.html', {'item':item,'workers':workers,'path':request.path.replace("/","+")},RequestContext(request))
@login_required
def save_edited_asset(request,id):
    lang=select_language(request)
    item_type = {'mezuza':Mezuza,
                'tfilin':Tfilin}
    data = request.POST
    try:
        item = item_type[data.get('asset_type')].objects.get(id=id)
    except item_type[data.get('asset_type')].DoesNotExist, KeyError:
        pass
    item.description=data.get('description_'+id)
    item.worker=Person.objects.get(id=data.get('worker_'+id))
    item.payment=data.get('payment_'+id)
    item.save()
    item_name = {'mezuza':'Мезуза',
                'tfilin':'Тфилин'}
    item.name=item_name[data.get('asset_type')]
    item.price = item.payment
    item.item_type = data.get('asset_type')
    return render_to_response(languages[lang]+'edited_asset.html', {'item':item,'path':request.path.replace("/","+")},RequestContext(request))
    
    
    
    
@login_required
def new_worker(request):
    lang=select_language(request)
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError
    method = request.method
    if request.method == 'POST':
        form = UserCreationFormMY(request.POST)
        # a= form.is_valid()
        # raise TypeError
        if form.is_valid():
            data = form.cleaned_data
            c=Person(fio=data['fio'], 
                    tel = data['tel'],
                    mail = data['mail'],
                    login = data['username'])
            c.save()
            # raise ImportError
            return render_to_response(languages[lang]+'OK.html', {'path':request.path.replace("/","+")},RequestContext(request))
    else:
        form = l_forms[lang]['UserCreationFormMY']()
    return render_to_response(languages[lang]+'new_ticket_headless.html', {'form':form,'form_id':'new_worker', 'method':method,'path':request.path.replace("/","+")},RequestContext(request))
            
@login_required
def debt(request,claim_id,adding):
    try:
        c=Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        request.session['my_error'] = u'Нет такого заказа. Номер %s!' % claim_id
        return HttpResponseRedirect("/") 
    client=c.for_client.get()
    c.get_cash+=int(adding)
    c.date_of_payment=datetime.datetime.now()
    c.save()
    return HttpResponseRedirect("/client_claims/"+str(client.id))
@login_required
def print_claim(request,claim_id):
    lang=select_language(request)
    user = request.user.username
    try:
        manager = Person.objects.get(login=user)
    except Person.DoesNotExist:
        manager = FioError()
    try:
        c=Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        request.session['my_error'] = u'Нет такого заказа. Номер %s!' % claim_id
        return HttpResponseRedirect("/")
    full_pay=0
    got_pay=0
    ms = c.mezuza.all()
    ts = c.tfilin.all()
    b=False
    if c.bdikot.count():
        b = c.bdikot.get()
        full_pay+=b.payment
    for m in ms:
        full_pay+=m.payment
    for t in ts:
        full_pay+=t.payment
    c.rest_cash = full_pay-c.get_cash-c.discount
    c.payment = full_pay-c.discount
    c.full_pay=full_pay
    return render_to_response(languages[lang]+'print_payment.html', {'now':datetime.datetime.now(),'worker':manager,'manager':manager, 'claim':c,'mezuzas':ms,'tfilins':ts,'bdika':b,'path':request.path.replace("/","+")},RequestContext(request))
def delete_claim(request,claim_id):
    user = request.user.username
    try:
        manager = Person.objects.get(login=user)
    except Person.DoesNotExist:
        manager = FioError()
    try:
        c=Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        request.session['my_error'] = u'Нет такого заказа. Номер %s!' % claim_id
        return HttpResponseRedirect("/")
    client = c.for_client.get()
    ms = c.mezuza.all()
    ts = c.tfilin.all()
    if c.bdikot.count():
        b = c.bdikot.get()
        b.delete()
    for m in ms:
        m.delete()
    for t in ts:
        t.delete()
    c.delete()
    return HttpResponseRedirect("/client_claims/"+str(client.id))  
    
    
    
def select_language(request):
    if request.session.get('language'):
        lang = request.session.get('language')
    else:
        lang='ru'
    return lang
    
    
@login_required
def set_reminder(request,task_type,task_id):
    if not acl(request,task_type,task_id):
        request.session['my_error'] = u'Нет права доступа к этой задаче!'
        return HttpResponseRedirect("/tasks/")
    user = request.user.username
    method = request.method
    data = 0
    time = 0
    try:
        task_full = task_types[task_type].objects.get(id = task_id)
    except:
        request.session['my_error'] = u'Задача почему-то не найдена. Номер ошибки set_reminder_125!'
        return HttpResponseRedirect('/tasks/')
    if request.method == 'POST':
        if 'datepicker' in request.POST:
            data = request.POST['datepicker']
        if 'time' in request.POST:
            time = request.POST['time']
        dtt = datetime.datetime(*map(int,([data.strip().split('/')[2],data.strip().split('/')[1],data.strip().split('/')[0]]+time.strip().split(':'))))
        task_full.when_to_reminder = dtt
        task_full.save()
        set_last_activity(user,request.path)
        return HttpResponseRedirect('/tasks/')
    else:
        after_hour = str(datetime.datetime.now().hour+1)+":"+str(datetime.datetime.now().minute)
        today = str(datetime.datetime.now().day)+"/"+str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().year)
    set_last_activity(user,request.path)
    return render_to_response(languages[lang]+'set_reminder.html', {'method':method,'today':today,'after_hour':after_hour},RequestContext(request))
@login_required
def move_to_call(request,task_type,task_id):
    if not acl(request,task_type,task_id):
        request.session['my_error'] = u'Нет права доступа к этой задаче!'
        return HttpResponseRedirect("/tasks/")
    user = request.user.username
    method = request.method
    data = 0
    time = 0
    try:
        task_full = task_types[task_type].objects.get(id = task_id)
    except:
        return HttpResponseRedirect('/tasks/')
    if request.method == 'POST':
        if 'datepicker' in request.POST:
            data = request.POST['datepicker']
        if 'time' in request.POST:
            time = request.POST['time']
        dtt = datetime.datetime(*map(int,([data.strip().split('/')[2],data.strip().split('/')[1],data.strip().split('/')[0]]+time.strip().split(':'))))
        task_full.when_to_reminder = dtt
        cat_call = Categories.objects.get(name = 'Звонки')
        task_full.category = cat_call
        task_full.save()
        set_last_activity(user,request.path)
        return HttpResponseRedirect('/tasks/')
    else:
        after_hour = str(datetime.datetime.now().hour+1)+":"+str(datetime.datetime.now().minute)
        today = str(datetime.datetime.now().day)+"/"+str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().year)
    set_last_activity(user,request.path)
    return render_to_response(languages[lang]+'set_reminder.html', {'method':method,'today':today,'after_hour':after_hour},RequestContext(request))
@login_required    
def change_language(request,lang,address_to_return):
    request.session['language']=lang
    if not address_to_return:
        return HttpResponseRedirect("/")
    # return HttpResponseRedirect('/')
    address_to_return = address_to_return.replace("+",'/')
    return HttpResponseRedirect(address_to_return)
# @login_required    
def change_language_root(request,lang):
    request.session['language']=lang
    return HttpResponseRedirect("/")

@login_required    
def register(request):
    lang=select_language(request)
    if request.method == 'POST':
        form = UserCreationFormMY(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_user = form.save()
            new_person = Person(
                fio = data['fio'],
                tel = data['tel'],
                mail = data['mail'],
                login = data['username']
            )
            new_person.save()
            return HttpResponseRedirect("/")
    else:
        form = l_forms[lang]['UserCreationFormMY']()
    return render_to_response(languages[lang]+"registration/register.html",{'form':form,'path':request.path.replace("/","+")},RequestContext(request))
@login_required    
def profile(request):
    user = request.user.username
    set_last_activity(user,request.path)
    return HttpResponseRedirect("/tasks/")
@login_required
def clients(request):
    # получаем ошибку, если она установлена и сбрасываем её в запросах
    if request.session.get('my_error'):
        my_error = [request.session.get('my_error'),]
    else:
        my_error=[]
    lang = select_language(request)
    print lang
    request.session['my_error'] = ''
    user = request.user.username
    method = request.method
    if  request.method == 'POST':
        pass
    else:
        try:
            worker = Person.objects.get(login=user)
        except Person.DoesNotExist:
            worker = 'Нет такого пользователя'
        # получаем заявки ДЛЯ человека
        # просроченные
        # Получаем клиентов, у которых стоит напоминалка
        #clients_to_show = Client.objects.filter(deleted = False).filter(exit_date__isnull=True).filter(when_to_reminder__lt=datetime.datetime.now())
        ms=Mezuza.objects.filter(date_of_last_check__lt=datetime.datetime.now().replace(year=datetime.datetime.now().year - 1))
        ts=Tfilin.objects.filter(date_of_last_check__lt=datetime.datetime.now().replace(year=datetime.datetime.now().year - 1))
        clients_to_show=set()
        a1 = set(ms)
        if ts:
            a1.update(set(ts))
        for c in a1:
            clients_to_show.add(c.owner)
        #for c in ts:
        #    clients_to_show.add(c.owner_for_tfilin.get())
        # clients_to_show = ''# если задач нет - вывести это в шаблон        
        # получаем кол-во клиентов в этот раз и сравниваем с тем, что было для уведомления всплывающим окном или ещё какой фигней
        
        alert = False
        if request.session.get('clients_number'):
            clients_number_was = int(request.session.get('clients_number'))
        else:
            clients_number_was = 999
        clients_number = len(clients_to_show)
        if clients_number_was < clients_number:
            alert = True
        request.session['clients_number'] = clients_number
        # только для админов
        admin = False
        if user in admins:
            admin = True
            pass
    #set_last_activity(user,request.path)
    return render_to_response(languages[lang]+'tasks.html',{'my_error':my_error,'user':user,'worker':worker,'clients_to_show':clients_to_show,'alert':alert,'path':request.path.replace("/","+")},RequestContext(request))
@login_required
def client(request,client_id):
    lang=select_language(request)

    #if not acl(request,task_type,task_id):
    #    request.session['my_error'] = u'Нет права доступа к этой задаче!'
    #    return HttpResponseRedirect("/tasks/")
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    try:
        # есть ли здача или она уже удалена?
        try:
            client_full = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            request.session['my_error'] = u'Нет такого заказа. Номер %s!' % claim_id
            return HttpResponseRedirect("/")
        try:
            tmp_notes = Note.objects.filter(for_client=client_full).order_by('-timestamp')
        except Note.DoesNotExist:
            tmp_notes = ('Нет подходящих заметок',)
        notes=[]
        for note in tmp_notes:
            notes.append(note_with_indent(note,0))
            build_note_tree(note,notes,1)
        # подготовка к выводу
        client_full.html_description = htmlize(client_full.description)
        method = request.method
        files=client_full.file.all()
        if request.method == 'POST':
            form = NoteToClientAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if request.POST.get('add_comment'):
                    note = Note(
                        timestamp = datetime.datetime.now(),
                        note = data['note'],
                        author = fio
                    )
                    note.save()
                    note.for_client.add(client_full)
                    note.save()
                    return HttpResponseRedirect(request.get_full_path())
                elif request.POST.get('answer_to_comment'):
                    parent_note = Note.objects.get(id=int(request.POST.get('to_note')))
                    note = Note(
                        timestamp = datetime.datetime.now(),
                        note = request.POST.get('answer'),
                        author = fio,
                    )
                    note.save()
                    note.parent_note.add(parent_note)
                    note.save()
                    return HttpResponseRedirect(request.get_full_path())
                elif request.POST.get('del_comment'):
                    note_to_del_id=request.POST.get('num')
                    note_to_del = Note.objects.get(id=note_to_del_id)
                    # Если есть дочерние комментарии - прикрепить к родительской заметке или к задаче
                    children_note=''
                    parent_note=''
                    try:
                        children_note = note_to_del.children_note.get()
                    except Note.DoesNotExist:
                        pass
                    try:
                        parent_note= note_to_del.parent_note.get()
                    except Note.DoesNotExist:
                        pass
                    # Если есть дочерний комментарий - работаем
                    if children_note:
                        # Если есть родительский комментарий - прикрепляем к нему
                        if parent_note:
                            parent_note.children_note.add(children_note)
                            parent_note.save()
                        # Если родительского комментария нет - прикрепляем к задаче
                        else:
                            children_note.for_client.add(client_full)
                            children_note.save()
                    note_to_del.delete()
                    #set_last_activity(user,request.path)
                    return HttpResponseRedirect(request.get_full_path())
                elif request.POST.get('edit_comment'):
                    note_to_edit_id = request.POST.get('num')
                    for note in notes:
                        if note.id != int(note_to_edit_id):
                            note.note = htmlize(note.note)
                    #set_last_activity(user,request.path)
                    return render_to_response(languages[lang]+'task.html',{'files':files,'user':user,'worker':fio,'fio':fio,'task':client_full,'notes':notes, 'form':form,'note_to_edit_id':int(note_to_edit_id),'path':request.path.replace("/","+")},RequestContext(request))
                elif request.POST.get('save_edited_comment'):
                    note_to_edit_id = request.POST.get('num')
                    note_to_edit = Note.objects.get(id=note_to_edit_id)
                    old_comment = note_to_edit.note
                    note_to_edit.note = request.POST.get('text_note_to_edit')
                    note_to_edit.save()
                    #send_email_alternative(u"Отредактирован комментарий к задаче: "+task_full.name,u"Старый комментарий:"+old_comment+u"\nНовый комментарий"+note_to_edit.note+u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/"+task_addr[task_type]+"/"+str(task_full.id),[task_full.worker.mail,task_full.client.mail],fio)
                    #set_last_activity(user,request.path)
                    return HttpResponseRedirect(request.get_full_path())

        else:
            form = l_forms[lang]['NoteToClientAddForm']()
            for note in notes:
                note.note = htmlize(note.note)
            #set_last_activity(user,request.path)
            if client_full.dr:
                client_full.age=(datetime.datetime.now().date()-client_full.dr).days//365
            if client_full.spouse_dr:
                client_full.spouse_age=(datetime.datetime.now().date()-client_full.spouse_dr).days//365
            return render_to_response(languages[lang]+'task.html',{'files':files,'user':user,'fio':fio,'worker':fio,'task':client_full,'notes':notes, 'form':form,'path':request.path.replace("/","+")},RequestContext(request))
    # если задачи нет - возвращаем к списку с ошибкой
    except Client.DoesNotExist:
        # print 'here'
        # return tasks(request, my_error=u'Такой задачи нет. Возможно она была уже удалена')
        request.session['my_error'] = u'Такого клиента нет. Возможно он был удалён'
        return HttpResponseRedirect('/')
    # никогда не выполняется. нужно только для проформы
    return HttpResponseRedirect("/")

@login_required
def close_task(request,task_to_close_id):
    if not acl(request,'one_time',task_to_close_id):
        request.session['my_error'] = u'Нет права доступа к этой задаче!'
        return HttpResponseRedirect("/tasks/")

    task_to_close = Task.objects.get(id=task_to_close_id)
    method = request.method
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    try:
        tmp_notes = Note.objects.filter(for_task=task_to_close).order_by('-timestamp')
    except Note.DoesNotExist:
        tmp_notes = ('Нет подходящих заметок',)
    notes=[]
    for note in tmp_notes:
	notes.append(note_with_indent(note,0))
	build_note_tree(note,notes,1)
    # если закрываем заявку
    if request.method == 'POST':
        form = TicketClosingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            task_to_close.pbw=data['pbw']
            task_to_close.done_date=data['done_date']
            task_to_close.percentage=100
            task_to_close.save()
            request.session['my_error'] = u'Задача благополучно закрыта! Ещё одну? ;)'
            send_email_alternative(u"Задача закрыта и требует подтверждения: "+task_to_close.name,u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/one_time/"+str(task_to_close.id),[task_to_close.client.mail,]+admins_mail,fio)
            return HttpResponseRedirect('/tasks/')
    # если хотим закрыть заявку
    else: 
        # проверяем, есть ли незакрытые дочерние заявки. Если есть - выводим их список на новой странице
        try:
            not_closed_children_tasks = Task.objects.filter(deleted = False).filter(parent_task = task_to_close).exclude(percentage__exact=100)
        except:
            not_closed_children_tasks = ''
        if not_closed_children_tasks:
            set_last_activity(user,request.path)
            return render_to_response('not_closed_children.html', {'user':user,'fio':fio,'task_to_close':task_to_close,'not_closed_children_tasks':not_closed_children_tasks},RequestContext(request))
        form = TicketClosingForm({'done_date' : datetime.datetime.now(),})
    task_to_close.description = htmlize(task_to_close.description)
    for note in notes:
        note.note = htmlize(note.note)
    set_last_activity(user,request.path)
    return render_to_response('close_ticket.html', {'user':user,'fio':fio,'form':form, 'task':task_to_close,'notes':notes},RequestContext(request))
@login_required
def unclose_task(request,task_to_unclose_id):
    if not acl(request,'one_time',task_to_unclose_id):
        request.session['my_error'] = u'Нет права доступа к этой задаче!'
        return HttpResponseRedirect("/tasks/")

    try:
        task_to_unclose = Task.objects.get(id=task_to_unclose_id)
    except:
        task_to_unclose = ''
    method = request.method
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    task_to_unclose.percentage = 50
    task_to_unclose.save()
    send_email(u"Задача открыта заново: "+task_to_unclose.name,u"\nПосмотреть задачу можно тут:\nhttp://192.168.1.157:8080/task/"+str(task_to_unclose.id),[task_to_unclose.client.mail,task_to_unclose.worker.mail]+admins_mail)
    set_last_activity(user,request.path)
    return HttpResponseRedirect('/tasks/')
@login_required
def to(request, to_who):
    user = request.user.username
    method = request.method
    if request.session.get('my_error'):
        my_error = [request.session.get('my_error'),]
    else:
        my_error=[]
    request.session['my_error'] = ''
    if user not in admins:
        return HttpResponseRedirect("/tasks/")
    tasks = list()
    for task_type in task_types:
        if task_type != 'regular':
            for task in task_types[task_type].objects.filter(deleted = False).filter(percentage__lt=100).filter(start_date__lt=datetime.datetime.now()).filter(when_to_reminder__lt=datetime.datetime.now()).filter(category=Categories.objects.get(name=to_who).id):
                task.task_type=task_type
                tasks.append(task)
        else:
            for task in task_types[task_type].objects.filter(deleted = False).filter(next_date__lt=datetime.datetime.now()).filter(when_to_reminder__lt=datetime.datetime.now()).filter(category=Categories.objects.get(name=to_who).id):
                task.task_type=task_type
                tasks.append(task)
    tasks_to = list(chain(tasks))
    notes={}
    for task in tasks_to:
        task.description = htmlize(task.description)
        try:
            notes[task.id] = Note.objects.filter(for_task=task).order_by('-timestamp')
        except Note.DoesNotExist:
            notes = ('Нет подходящих заметок',)
    for note_to_id in notes:
        for note in notes[note_to_id]:
            note.note = htmlize(note.note)
    set_last_activity(user,request.path)
    return render_to_response('tasks_to.html', {'tasks':tasks_to,'notes':notes,'to_who':to_who, 'method':method},RequestContext(request))
@login_required
def confirm_task(request,task_to_confirm_id):
    user = request.user.username
    if user not in admins:
        request.session['my_error'] = u'Нет права подтвердить закрытие задачи!'
        return HttpResponseRedirect("/tasks/")

    task_to_confirm = Task.objects.get(id=task_to_confirm_id)
    method = request.method
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError()
    if request.method == 'POST':
        form = TicketConfirmingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if request.POST.get('confirm_task'):
                task_to_confirm.confirmed=data['confirmed']
                task_to_confirm.confirmed_date=data['confirmed_date']
                task_to_confirm.save()
                request.session['my_error'] = u'Выполнение задачи успешно подтверждено!'
                send_email(u"Завершение задачи подтверждено: "+task_to_confirm.name,u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/"+str(task_to_confirm.id),[task_to_confirm.worker.mail,task_to_confirm.client.mail])
                set_last_activity(user,request.path)
                return HttpResponseRedirect('/tasks/')
            elif request.POST.get('del_comment'):
                note_to_del_id=request.POST.get('num')
                note_to_del = Note.objects.get(id=note_to_del_id)
                note_to_del.delete()
                set_last_activity(user,request.path)
                return HttpResponseRedirect(request.get_full_path())
    else:
        try:
            notes = Note.objects.filter(for_task=task_to_confirm).order_by('-timestamp')
        except Note.DoesNotExist:
            notes = ('Нет подходящих заметок',)
        form = TicketConfirmingForm({'confirmed':True, 'confirmed_date':datetime.datetime.now()})
        for note in notes:
            note.note = htmlize(note.note)
    task_to_confirm.description = htmlize(task_to_confirm.description)
    set_last_activity(user,request.path)
    return render_to_response('confirm_ticket.html', {'form':form,'task':task_to_confirm,'notes':notes,'method':method,'fio':fio},RequestContext(request))    
    
@login_required
def image_delete(request,file_id):
    lang = select_language(request)
    file = File.objects.get(id=file_id)
    client = file.for_client.get()
    
    storage, path = file.file.storage, file.file.path
    storage.delete(path)
    
    # raise TabError
    file.delete()
    return HttpResponseRedirect("/client/"+str(client.id)+"/")
@login_required
def edit_client(request,client_id):
    lang = select_language(request)
    #if not acl(request,'one_time',task_to_edit_id):
    #   request.session['my_error'] = u'Нет права доступа к этой задаче!'
    #    return HttpResponseRedirect("/tasks/")
    user = request.user.username
    try:
        fio = Person.objects.get(login=user)
    except Person.DoesNotExist:
        fio = FioError
    method = request.method
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        request.session['my_error'] = u'Нет такого клиента. Номер %s!' % client_id
        return HttpResponseRedirect("/")    
    if request.method == 'POST':
        form = EditClientForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            client.fio=data['fio']
            client.description=data['description']
            client.entering_date=data['entering_date']
            client.exiting_date=data['exiting_date']
            client.mail=data['mail']
            client.tel=data['tel']
            client.dr=data['dr']
            client.spouse_fio=data['spouse_fio']
            client.spouse_tel=data['spouse_tel']
            client.spouse_mail=data['spouse_mail']
            client.spouse_dr=data['spouse_dr']
            client.address=data['address']
            client.home_tel=data['home_tel']
            client.save()
            if request.FILES:
                client.file.add(save_file(request.FILES,client.id))
            client.save()
            return HttpResponseRedirect("/client/"+str(client.id))
    else:
        form = l_forms[lang]['EditClientForm']({'fio':client.fio,
                            'description':client.description,
                            'entering_date':client.entering_date,
                            'exiting_date':client.exiting_date,
                            'mail':client.mail,
                            'tel':client.tel,
                            'dr':client.dr,
                            'spouse_fio':client.spouse_fio,
                            'spouse_tel':client.spouse_tel,
                            'spouse_mail':client.spouse_mail,
                            'spouse_dr':client.spouse_dr,
                            'address':client.address,
                            'home_tel':client.home_tel,
                            'file':client.file.all(),
                            })
    
    return render_to_response(languages[lang]+'edit_ticket.html', {'worker':fio,'form':form, 'method':method,'path':request.path.replace("/","+").replace("/","+")},RequestContext(request))
@login_required
def delete_task(request,task_type,task_to_delete_id):
    user = request.user.username
    task_to_delete = task_types[task_type].objects.get(id=task_to_delete_id)
    task_to_delete.deleted = True
    task_to_delete.save()
    set_last_activity(user,request.path)
    return HttpResponseRedirect('/tasks/')
@login_required
def undelete_task(request,task_type,task_id):
    task = task_types[task_type].objects.get(id=task_id)
    task.deleted = False
    task.save()
    set_last_activity(user,request.path)
    return HttpResponseRedirect('/tasks/')    
@login_required
def completle_delete_task(request,task_type,task_to_delete_id):
    user = request.user.username
    if user not in admins:
        return HttpResponseRedirect("/tasks/")
    task_to_delete = task_types[task_type].objects.get(id=task_to_delete_id)
    task_to_delete.delete()
    set_last_activity(user,request.path)
    return HttpResponseRedirect('/tasks/')
@login_required
def deleted_tasks(request):
    user = request.user.username
    if user not in admins:
        return HttpResponseRedirect("/tasks/")
    try:
        tasks = list()
        for task_type in task_types:
            for task in task_types[task_type].objects.filter(deleted = True):
                task.task_type=task_type
                tasks.append(task)
        tasks = list(chain(tasks))
    except:
        task = ('Нет таких задач',)
    set_last_activity(user,request.path)
    return render_to_response('deleted_tasks.html', {'tasks':tasks,},RequestContext(request))
def send_email(subject,message,to):
    good_mails=[mail for mail in to if mail!='']
    send_mail(subject,message,"meoc-it@mail.ru",good_mails)

@login_required
def all_clients(request):
    lang=select_language(request)
    def find_parent_task(note):
        """
        Поиск родительской заявки для примечания
        """
        try:
            if note.parent_note:
                return find_parent_task(note.parent_note.get())
        except Note.DoesNotExist:
            return Client.objects.filter(note = note)
    user = request.user.username
    not_finded = False
    finded_tasks = ''
    method = request.method
    if request.method == 'POST':
        form = ClientSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            finded_client_notes=''
            finded_client_names=''
            finded_client_desc=''
            try:
                finded_client_names = Client.objects.filter(fio__icontains = data['name'])
            except:
                pass
            try:
                finded_client_desc = Client.objects.filter(description__icontains = data['name'])
            except:
                pass
            try:
                notes = Note.objects.filter(note__icontains = data['name'])
            except:
                pass
            for note in notes:
                finded_client_notes = find_parent_task(note = note)
            finded_clients = list(chain(finded_client_names, finded_client_desc, finded_client_notes))
            if not finded_clients:
                not_finded = True
            #set_last_activity(user,request.path)
            return render_to_response(languages[lang]+'all_tasks.html', {'not_finded':not_finded,'finded_tasks':finded_clients,'form':form, 'method':method,'path':request.path.replace("/","+")},RequestContext(request))
    else:
        form = l_forms[lang]['ClientSearchForm']()
        if request.session.get('my_error'):
            my_error = [request.session.get('my_error'),]
        else:
            my_error=[]
        request.session['my_error'] = ''
        try:
            # отображаем все НЕ закрытые заявки, т.е. процент выполнения которых меньше 100
            clients = Client.objects.filter(deleted = False)
        except:
            tasks = ''# если задач нет - вывести это в шаблон
    #set_last_activity(user,request.path)
    return render_to_response(languages[lang]+'all_tasks.html', {'my_error':my_error,'tasks':clients,'form':form, 'method':method,'path':request.path.replace("/","+")},RequestContext(request))
@login_required
def add_children_task(request,parent_task_type,parent_task_id):
    method = request.method
    user = request.user.username
    try:
        # находим родительскую задачу
        parent_task = task_types[parent_task_type].objects.get(id=parent_task_id)
    except:
        my_error=request.session.get('my_error')# если задач нет - вывести это в шаблон
        my_error.append('Не найдена родительская задача?!')
        return HttpResponseRedirect('/tasks/')
    if request.method == 'POST':
        form = NewTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            t=Task(name=data['name'], 
                pbu=data['pbus'], 
                description=data['description'], 
                client=data['clients'], 
                priority=data['priority'], 
                category=data['category'], 
                start_date=data['start_date'],
                when_to_reminder = data['start_date'],
                due_date=data['due_date'], 
                worker=data['workers'],
                percentage=data['percentage'],
                acl = data['clients'].login+';'+data['workers'].login)
            t.save()
            if parent_task_type =='one_time':
                t.parent_task.add(parent_task)
            if parent_task_type =='regular':
                t.parent_regular_task.add(parent_task)
            t.save()
            # отправляем уведомление исполнителю по мылу
            send_email(u"Новая подзадача: "+t.name+u" для задачи "+parent_task.name,t.description+u"\nПосмотреть подзадачу можно тут:\nhttp://"+server_ip+"/task/"+str(t.id)+u"\nПосмотреть задачу можно тут:\nhttp://"+server_ip+"/task/"+str(parent_task.id),[data['workers'].mail,])
            set_last_activity(user,request.path)
            return HttpResponseRedirect('/tasks/')
    else:
        form = NewTicketForm({'percentage':0,'start_date':datetime.datetime.now(),'due_date':datetime.datetime.now(),'priority':parent_task.priority,'category':parent_task.category})
    set_last_activity(user,request.path)
    return render_to_response('new_ticket.html', {'form':form, 'method':method},RequestContext(request))
@login_required
def regular_task_done(request,task_id):
    user = request.user.username
    method = request.method
    try:
        # находим задачу
        task = RegularTask.objects.get(id=task_id)
    except:
        my_error=request.session.get('my_error')# если задач нет - вывести это в шаблон
        my_error.append('Не найдена задача?!')
        return HttpResponseRedirect('/tasks/')
    task.next_date = generate_next_reminder(decronize(task.period), task.stop_date)
    task.when_to_reminder = task.next_date
    task.save()
    set_last_activity(user,request.path)
    return HttpResponseRedirect('/tasks/')

@login_required
def get_all_logged_in_users(request):
    user = request.user.username
    if user in admins:
        last_activities=get_last_activities()
        return render_to_response('logged_in_user_list.html', {'last_activities':last_activities,},RequestContext(request))
