from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.db import models

#object does not exist
from django.core.exceptions import ObjectDoesNotExist

#python and django serializers
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json

#csrf token
from django.views.decorators.csrf import ensure_csrf_cookie

#import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

#import transaction
from django.db import transaction

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

#import models
from socialnetwork3.models import *

#import forms
from socialnetwork3.forms import *

#use time
from datetime import datetime
import time

from django.template import RequestContext

import inspect

# Create your views here.
@ensure_csrf_cookie
@login_required
def home(request):
	all_info = Messages.objects.values('id','user_id', 'post', 'date', 'user__last_name', 'user__first_name', 'user__username').order_by('-date')
	profile = get_list_or_404(Profile.objects.filter(user=request.user).values('user__last_name','user_id', 'user__first_name', 'user__username', 'age', 'bio','picture'))
	context = {'messages': all_info, 'profile': profile[0]}
	return render(request, 'socialnetwork3/global.html', context)

@login_required
def getstream(request):
	all_messages = Messages.objects.values('id', 'user_id', 'post', 'date', 'user__last_name', 'user__first_name', 'user__username').order_by('-date')
	tryjson = []
	for x in all_messages:
		comments_to_x = Comments.objects.filter(relatedmessage=x['id']).values('commentdate', 'comment', 'user_id', 'user__last_name', 'user__first_name').order_by('commentdate')
		#print comments_to_x
		comments = []
		for y in comments_to_x:
			comments.append(y)
		a = {'id': x['id'], 'user_id': x['user_id'], 'post': x['post'], 'date': x['date'], 'last_name': x['user__last_name'], 'first_name': x['user__first_name'], 'username': x['user__username'], 'comments': comments}
		tryjson.append(a)
	jsonobj = json.dumps(tryjson, cls=DjangoJSONEncoder)
	print jsonobj
	return HttpResponse(jsonobj, content_type='application/json')

@login_required
def create(request):
	if not request.POST['input-content']:
		return render(request, 'socialnetwork3/global.html', {'errors': 'You have to create content'})
	else:
		#create a new instance of Messages
		print 'create new content'
		message = Messages()
		message.user = request.user
		message.post = request.POST['input-content'][:200]
		message.save()
	return redirect(reverse('home'))

@login_required
@ensure_csrf_cookie
def create_ajax(request):
	errors = []

	if not request.POST['content']:
		message = 'You must create some content'
		json_error = '{ "error": "'+message+'" }'
		return HttpResponse(json_error, content_type='application/json')

	message = Messages()
	message.user = request.user
	message.post = request.POST['content'][:200]
	message.save()
	return HttpResponse('{ "success": "true" }', content_type='application/json')

@login_required
@ensure_csrf_cookie
def create_comment_ajax(request):
	errors = []

	if not request.POST['comment']:
		message = 'You must input a comment'
		json_error = '{ "error": "'+message+'" }'
		return HttpResponse(json_error, content_type='application/json')

	relate_message = Messages.objects.get(id=request.POST['comment_to_message'])
	new_comment = Comments()
	new_comment.user = request.user
	new_comment.relatedmessage = relate_message
	new_comment.comment = request.POST['comment']
	new_comment.save()
	return HttpResponse('{ "success": "true" }', content_type='application/json')



@login_required
def profile(request):
	if request.GET.get('username', False):
		if not 'username' in request.GET:
			return render(request, 'socialnetwork3/global.html', {'errors': 'No user name'})

		username = request.GET['username']
		all_info = Messages.objects.filter(user__username=username).values('user_id', 'post', 'date', 'user__last_name', 'user__first_name', 'user__username').order_by('-date')
		profile = get_list_or_404(Profile.objects.filter(user__username=username).values('user__last_name','user_id', 'user__first_name', 'user__username', 'age', 'bio','picture'))
		context = {'messages': all_info, 'profile': profile[0]}
		return render(request, 'socialnetwork3/profile.html', context)
	if request.POST.get('username', False):
		if not 'username' in request.POST:
			return render(request, 'socialnetwork3/global.html', {'errors': 'No user name'})

		username = request.POST['username']
		all_info = get_list_or_404(Messages.objects.filter(user__username=username).values('user_id', 'post', 'date', 'user__last_name', 'user__first_name', 'user__username').order_by('-date'))
		profile = get_list_or_404(Profile.objects.filter(user__username=username).values('user__last_name','user_id', 'user__first_name', 'user__username', 'age', 'bio','picture'))
		context = {'messages': all_info, 'profile': profile[0]}
		return render(request, 'socialnetwork3/profile.html', context)
	if request.POST.get('follow', False):
		follow = Follow()
		follow.user = request.user
		follow.follows = request.POST.get('followuser', False)
		follow.save()
		return redirect(reverse('home'))
	if request.POST.get('unfollow', False):
		followuser = request.POST.get('followuser', False)
		try:
			Follow.objects.filter(user=request.user).filter(follows=followuser).delete()
		except:
			raise Http404('No such user')
		return redirect(reverse('home'))


@login_required
def followstream(request):
	follows = Follow.objects.filter(user=request.user)
	following_message = Messages.objects.none()

	try:
		for p in follows:
			following_message1 = Messages.objects.filter(user__username=p.follows).values('user_id', 'post', 'date', 'user__last_name', 'user__first_name', 'user__username',)
	 		following_message = following_message | following_message1
		#print following_message
		following_message = following_message.order_by('-date')
		profile = Profile.objects.filter(user=request.user).values('user__last_name','user_id', 'user__first_name', 'user__username', 'age', 'bio','picture')
		context = {'messages': following_message, 'profile': profile[0]}
		return render(request, 'socialnetwork3/followstream.html', context)
	except:
		raise Http404('No follow user found')
		
	
	
	# following_message = following_message.order_by('-date')
	
	# profile = Profile.objects.filter(user=request.user).values('user__last_name','user_id', 'user__first_name', 'user__username', 'age', 'bio','picture')
	# context = {'messages': following_message, 'profile': profile[0]}
	# return render(request, 'socialnetwork3/followstream.html', context)

@login_required
@transaction.atomic
def editprofile(request):
	try:
		if request.method == 'GET':
			profile = Profile.objects.get(user=request.user)
			form = EditProfile(instance=profile)
			context = {'form': form}
			return render(request, 'socialnetwork3/editprofile.html', context)

		profile = get_object_or_404(Profile, user=request.user)
		form = EditProfile(request.POST, request.FILES, instance=profile)
		context = {}
		if not form.is_valid():
			context = {'form': form}
			return render(request, 'socialnetwork3/editprofile.html', context)
		else:
			try:
				print form
				if form.cleaned_data['picture'].content_type and form.cleaned_data['picture'].content_type.startswith('images'):
					profile.content_type = form.cleaned_data['picture'].content_type
			except:
				pass
			form.save()
			return redirect(reverse('home'))
			#return render(request, 'socialnetwork3/global.html', {})

	except Profile.DoesNotExist:
		return redirect(reverse('home'))

@login_required
def get_photo(request,id):
	user = get_object_or_404(User, id=id)
	return HttpResponse(user.profile.picture, content_type=user.profile.content_type)

@transaction.atomic
def register(request):
	context = {}

	if request.method == "GET":
		context['form'] = RegistrationForm()
		return render(request, 'socialnetwork3/register.html', context)

	form = RegistrationForm(request.POST)
	context['form'] = form

	if not form.is_valid():
		return render(request, 'socialnetwork3/register.html', context)

	new_user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password1'], first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'])
	new_user.is_active = False
	new_user.save()

	token = default_token_generator.make_token(new_user)

	email_body = """
Welcome to the WebApp Class Address Book.  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))
	
	send_mail(subject="Verify your email address", message= email_body,from_email="socialnetwork@cmu.edu",recipient_list=[new_user.email])

	context['email'] = form.cleaned_data['email']
	# new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
	# login(request, new_user)
	#return redirect(reverse('home'))
	return render(request, 'socialnetwork3/needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
	user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
	if not default_token_generator.check_token(user, token):
		raise Http404

    # Otherwise token was valid, activate the user.
	user.is_active = True
	user.save()
	return render(request, 'socialnetwork3/confirmed.html', {})


