import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('~/.virtualenvs/django/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/var/www/ishayahu/data/tasks')
#sys.path.append('/var')

os.environ['DJANGO_SETTINGS_MODULE'] = 'tasks.settings'

# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/django/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
