from django.shortcuts import render_to_response, render
from login.forms import *
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from login.models import *
import json
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from django.utils import timezone

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
                return HttpResponseRedirect('/home')
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
            if (len(Group.objects.filter(name = className)) == 0):
                content_type = ContentType.objects.get_for_model(User)
                permission = Permission.objects.create(
                    codename='owner_'+className,
                    name='owner for '+className,
                    content_type=content_type,
                )

                Group.objects.create(name=className)            #create new group
                request.user.user_permissions.add(permission)   #current user gets owner permission

                return HttpResponseRedirect('/course/page/?className=%s' % (className))
            else:
                return HttpResponse('groupname already taken') #todo, add comment in template about this
        else:
            if Group.objects.get(name=className):
                Group.objects.get(name=className).user_set.add(request.user)
                return HttpResponseRedirect('/course/page/?className=%s' % (className))
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
    group_name = request.GET.get('className')
    if request.method == "POST":
        if (Group.objects.filter(name=group_name)).count() == 1:
            user = request.user
            group = Group.objects.get(name = group_name)

            if (Slowdown.objects.filter(name = group_name).count() == 0):
                datetime_object = Datet.objects.create(name = user.username)
                slowdown_object = Slowdown.objects.create(name = user.username)
                membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datetime = datetime_object)
                membership_object.save()
                slowdown_object.save()
                return render_to_response('usersites/student.html')

            slowdown_object = Slowdown.objects.filter(name = user.username)

            if Membership.objects.filter(person = user, group = group).count() == 1:
                datetime_object = Datet.objects.create(name = user.username)
                last_datetime_object = slowdown_object.datetimes.order_by('-id')[0]
                if (last_datetime_object.datetime < datetime_object.datetime - timedelta(seconds=1)):
                    return HttpResponse('for rask ;)')
                else:
                    slowdown_object.datetimes.add(datetime_object)
                    membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datetime = datetime_object)
                    membership_object.save()
                    slowdown_object.save()
                    return render_to_response('usersites/student.html')
            else:
                datetime_object = Datet.objects.create(name = user.username)
                membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datetime = datetime_object)
                membership_object.save()
            return render_to_response('usersites/student.html')
        else:
            return HttpResponseRedirect('/course')
    else:
        return render_to_response('usersites/student.html')


@login_required(login_url='login')
def homepage_view(request):
    return render_to_response('homepage.html')

@login_required(login_url='login')
def teacher_view(request):
    group_name = request.GET.get('className')
    if (request.user.user_permissions.filter(codename='owner_'+group_name).count() == 1):
        if Membership.objects.filter(group = Group.objects.filter(name=group_name)).count() > 0:
            membership_objects = Membership.objects.filter(group = Group.objects.filter(name=group_name)[0])
            start_time = membership_objects[0].datetime.datetime

            total_count = membership_objects.count() #Henter ut antallet forespørsler i databasen
            data = membership_objects.values_list('datetime', flat=True)

            minutelist = {}
            for feedback in data:
                key = round((membership_objects[feedback-1].datetime.datetime - start_time).total_seconds()/60)
                if key in minutelist:
                    minutelist[key] += 1
                else:
                    minutelist[key] = 1

            list = [['Time', 'Slowdown pressed']]

            for i in range(0, 60, 2):
                count = 0
                if i in minutelist.keys():
                    count += minutelist[i]
                elif i - 1 in minutelist.keys():
                    count += minutelist[i - 1]
                list.append([i, count])

            variables = RequestContext(request, {'count': total_count, 'array':json.dumps(list), 'start_time':start_time}) #Gjør om til variabel som html forstår
            return render_to_response('usersites/teacher.html', variables) #Må sende variabel til dokumentet her
        render_to_response('usersites/teacher.html')
    return HttpResponseRedirect('/course') #Må sende variabel til dokumentet her

@login_required(login_url='login')
def user_view(request):
    context = RequestContext(request)
    if request.method == "POST":
        student = request.POST.get('student')

        if student:
            return HttpResponseRedirect('/usersites/student')
        else:
            return HttpResponseRedirect('/usersites/teacher')
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('/homepage.html', {}, context)

def test_view(request):
    class_start = datetime.datetime.now()-datetime.timedelta(hours=2)
    data = Slowdown.objects.filter(date__range=(class_start, datetime.datetime.now()))
    data = data.values_list('date', flat=True)
    minutelist = {}
    for feedback in data:
        key = 120-feedback.minute
        if key in minutelist:
            minutelist[key] += 1
        else:
            minutelist[key] = 1

    list = [['Time', 'Slowdown pressed']]

    for i in range(0, 127, 2):
        count = 0
        if i in minutelist.keys():
            count += minutelist[i]
        elif i-1 in minutelist.keys():
            count += minutelist[i-1]
        list.append([i, count])


    return render_to_response('usersites/testing.html', {'array': json.dumps(list)})

@login_required(login_url='login')
def joined_course_view(request):
    if Group.objects.get(name=request.GET.get('className', '/')):
        user = request.user
        group = Group.objects.get(name=request.GET.get('className', '/'))
        if (user.user_permissions.filter(codename='owner_'+group.name).count() == 1):
            return HttpResponseRedirect('/usersites/teacher/?className=%s' % (group.name))
        else:
            return HttpResponseRedirect('/usersites/student/?className=%s' % (group.name))
    else:
        return HttpResponseRedirect('/course')