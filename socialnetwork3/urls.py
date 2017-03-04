from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from socialnetwork3 import views as socialnetwork_views

urlpatterns = [
    url(r'^$', socialnetwork_views.home, name='home'),
    #default page
    url(r'^global$', socialnetwork_views.home, name='global'),
    #get stream using ajax
    url(r'^getstream$', socialnetwork_views.getstream, name='getstream'),
    #show all followers
    url(r'^followstream$', socialnetwork_views.followstream, name='followstream'),
    #create new post
    url(r'^create$', socialnetwork_views.create, name='create'),
    #create new post using ajax
    url(r'^create_ajax$', socialnetwork_views.create_ajax, name='create_ajax'),
    #create new comment using ajax
    url(r'^create_comment_ajax$', socialnetwork_views.create_comment_ajax, name='create_comment_ajax'),
    #route to login page
    url(r'^login$', auth_views.login, {'template_name':'socialnetwork3/login.html'}, name='login'),
    #logout
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    #route to profile page
    url(r'^profile$', socialnetwork_views.profile, name='profile'),
    url(r'^editprofile$', socialnetwork_views.editprofile, name='editprofile'),
    #route to register page
    url(r'^register$', socialnetwork_views.register, name='register'),
    #load the photo to the page
    url(r'^photo/(?P<id>\d+)$', socialnetwork_views.get_photo, name='photo'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$',
        socialnetwork_views.confirm_registration, name='confirm'),
]
