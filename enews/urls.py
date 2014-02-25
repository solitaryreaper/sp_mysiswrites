from django.conf.urls import patterns, url

from enews import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^trends/$', views.trends, name='trends'),
    url(r'^dailyjob/$', views.dailyjob, name='dailyjob'), 
    url(r'^bootstrapjob/$', views.bootstrapjob, name='bootstrapjob'),
    url(r'^trends/$', views.trends, name='trends'),                   
    url(r'^ingest/$', views.ingest, name='ingest'),    
    url(r'^ingest/(?P<url>.*)/$', views.ingest, name='ingest'),   
    url(r'^categorystats/$', views.get_category_stats, name='categorystats'),
    url(r'^timelinestats/$', views.get_timeline_stats, name='timelinestats'), 
    url(r'^feed/$', views.ArticlesFeed()),    
)