from django.shortcuts import render_to_response, render
from login.forms import *
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
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

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/login/success')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return render_to_response('login/login.html')

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login/login.html', {}, context)

@login_required(login_url='login')
def course_view(request):
    context = RequestContext(request)
    if request.method == "POST":
        className = request.POST.get('className')
        create = request.POST.get('create')

        if create:
            Group.objects.create(name=className)
            return HttpResponse("Created class:" + className)
        else:
            if Group.objects.get(name=className):
                Group.objects.get(name=className).user_set.add(request.user)
                return HttpResponse("Joined" + className)
            else:
                return HttpResponse("No class named: " + className)
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('courses/courses.html', {}, context)


@login_required(login_url='login')
def user_login_success(request):
    return render_to_response('login/success.html')

def user_logout_success(request):
    return render_to_response('login/logout_success.html')

@login_required(login_url='login')
def user_logout(request):

    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        logout(request)
        return HttpResponseRedirect('/')
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login/logout.html', {}, context)

@login_required(login_url='login')
def student_view(request):
    if request.method == "POST": #Refererer til html document sin action type, her har vi form method=post i htmldokumentet
        slowReq = Slowdown() #Klassen i models, husk å kjøre commands i notes
        slowReq.save() #Lagrer det til database, for å hente ut referer til Slowdown.objects
    return render_to_response('usersites/student.html')

@login_required(login_url='login')
def homepage_view(request):
    return render_to_response('homepage.html')

@login_required(login_url='login')
def teacher_view(request):
    slowReq = Slowdown.objects.count() #Henter ut antallet forespørsler i databasen
    variables = RequestContext(request, {'slowReq': slowReq}) #Gjør om til variabel som html forstår
    return render_to_response('usersites/teacher.html', variables) #Må sende variabel til dokumentet her

