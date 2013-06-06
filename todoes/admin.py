from django.contrib import admin
from todoes.models import Note,  File, Client, Categories, Person, Mezuza, Tfilin, Bdikot, Claim

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('fio','login','tel','mail','raiting')
class ClientAdmin(admin.ModelAdmin):
    list_display = ('fio','login','tel','mail','raiting')


#class TaskAdmin(admin.ModelAdmin):
#    search_fields = ('name', 'description', 'client', 'category', 'worker')
#    list_filter = ('client', 'start_date', 'due_date', 'done_date', 'priority', 'category', 'worker', 'pbw', 'pbu')
#    date_hierarchy = 'due_date'
#    ordering = ('-due_date', '-priority','worker')

admin.site.register(Note)
admin.site.register(File)
admin.site.register(Person, WorkerAdmin)
admin.site.register(Categories)
admin.site.register(Client)
admin.site.register(Claim)
admin.site.register(Tfilin)
admin.site.register(Bdikot)
admin.site.register(Mezuza)