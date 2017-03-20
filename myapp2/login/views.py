from django.shortcuts import render_to_response, render
from login.forms import *
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template import RequestContext
from login.models import *

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('register/register.html', variables)

def register_success(request):
    return render_to_response('register/success.html')

def index_view(request):
    return render_to_response('index.html')

def student_view(request):
    if request.method == "POST":
        slowReq = Slowdown()
        slowReq.save()
    return render_to_response('usersites/student.html')

def teacher_view(request):
    return render_to_response('usersites/teacher.html')


