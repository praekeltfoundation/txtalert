from django.conf.urls.defaults import *
from bookingtool import views

urlpatterns = patterns('',
    (r'availability\.js', views.availability),
)
