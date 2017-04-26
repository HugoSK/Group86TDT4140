#imports for views
from django.shortcuts import render_to_response                 #
from login.forms import *
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import json
from login.models import *
from django.contrib.contenttypes.models import ContentType
import datetime
from datetime import timedelta
from builtins import list as pylist
from django.utils import timezone

#view for register view
# -can find the form used in login.forms
def register_view(request):
    form = RegistrationForm()                       #get form from forms

    # check if registration form is sent in, if not handle with feedback
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():                         #check if user is valid
            new_user = User.objects.create_user(    #create user
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/home')
        else:
            variables = RequestContext(request, {'form': form, 'feedback':'Please fill out information correctly.'})
            return render_to_response('register/register.html', variables)

    variables = RequestContext(request, {'form': form})
    return render_to_response('register/register.html', variables)  #return statement, loads register.html template

#view for first page
# -loads the template, links to other parts of website
def index_view(request):
    return render_to_response('index.html')

#view for user login, used a open source solution
# -comments are from open source, slightly modified*
def user_login(request):
    # Obtain the context for the user's request.
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

#view for the lectures page (after logging in or registering)
# -@login_required, makes is so that the user must be signed in,
#  or it will be redirected to the login page
# -lists up all the current active lectures the user is in
@login_required(login_url='login')
def lecture_view(request):
    u = request.user            #request the current user object
    u_groups = u.groups.all()   #find the groups that the user participates in
    student_groups = []
    teacher_groups = []

    # append the group name in either teacher or student group
    for group in u_groups:
        if (u.user_permissions.filter(codename='owner_' + group.name).count() == 1):
            teacher_groups.append(group.name)
        else:
            student_groups.append(group.name)

    #set the variables for the render function
    variables = RequestContext(request, {'teacher_list':teacher_groups, 'student_list':student_groups})

    #check the user is trying to send information, validate
    if request.method == "POST":
        lecture_name = request.POST.get('lecture_name')
        create = request.POST.get('create')

        #check if the user pressed create or join
        if create:
            #check if the user haven't sent in illegal arguments
            if (Group.objects.filter(name = lecture_name).count() == 0):
                content_type = ContentType.objects.get_for_model(User)
                permission = Permission.objects.create(
                    codename='owner_'+lecture_name,
                    name='owner for '+lecture_name,
                    content_type=content_type,
                )

                Group.objects.create(name=lecture_name)         #create new group
                request.user.user_permissions.add(permission)   #current user gets owner permission

                #after the user have created the group/lecture, redirect to that lecture
                return HttpResponseRedirect('/lectures/page/?lecture_name=%s' % (lecture_name))
            else:
                variables = RequestContext(request, {'teacher_list': teacher_groups, 'student_list': student_groups,
                                                     'feedback':'lecture name already in use! Please try another'})
                return render_to_response('lectures/lecture.html', variables) #render the template with feedback

        #user pressed join:
        else:
            #check if lecture/group name is in the database:
            if (Group.objects.filter(name = lecture_name).count() == 1):
                Group.objects.get(name=lecture_name).user_set.add(request.user)
                #redirect to the lecture page
                return HttpResponseRedirect('/lectures/page/?lecture_name=%s' % (lecture_name))
            else:
                variables = RequestContext(request, {'teacher_list': teacher_groups, 'student_list': student_groups,
                                                     'feedback': 'Invalid lecture name! Please try another'})
                return render_to_response('lectures/lecture.html', variables)  # render the template with feedback
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('lectures/lecture.html', variables)

#view for user sign out
@login_required(login_url='login')
def user_logout(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        logout(request)                 #logout the current user
        return HttpResponseRedirect('/')#redirect to homepage
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login/logout.html', {}, context)

#view for the student inside a lecture
@login_required(login_url='login')
def student_view(request):
    group_name = request.GET.get('lecture_name') #get lecture name from url

    #if the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        #check if the group is valid, as one can send in another page in the url
        if request.POST['slowbtn'] == 'Slow down':
            if (Group.objects.filter(name=group_name)).count() > 0:

                user = request.user
                group = Group.objects.get(name = group_name)

                #if no student has pressed slow down button one can just make a new membership object
                if Membership.objects.filter(group = group).count() == 0:
                    #if the user is a student and the user is the first to join, safe to save to database
                    datetime_object = Datet.objects.create(name = user.username)
                    slowdown_object = Slowdown.objects.create(name = user.username)
                    membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datet = datetime_object)
                    membership_object.save()
                    slowdown_object.save()

                    questions = Question.objects.filter(lecture=group_name).values_list('questionText')
                    questions = list(reversed(questions))
                    form = QuestionForm()
                    return render_to_response('usersites/student.html', RequestContext(request, {
                                                                                                 'form': form,
                                                                                                 'questions': questions}))

                #check if the current user has pressed slow down and check if the user has pressed slow down in the last 10 seconds
                if Membership.objects.filter(person = user, group = group).count() > 0:
                    #create new datetime object and find the last datetime object
                    slowdown_object = Slowdown.objects.create(name=user.username)
                    last_datetime_object = Datet.objects.filter(name=user.username).order_by('-id')[0]

                    #check if user has submitted a slow down in the last 10 seconds
                    #  -TODO: last datetime object on this particular group, assessed not necessary
                    if (last_datetime_object.datet) > timezone.now()-timedelta(seconds=10):
                        questions = Question.objects.filter(lecture=group_name).values_list('questionText')
                        questions = list(reversed(questions))
                        form = QuestionForm()
                        return render_to_response('usersites/student.html', RequestContext(request, {'feedback': 'try again in a few seconds ... ',
                                                                                                     'form': form,
                                                                                                     'questions': questions}))
                        # render the template with feedback

                    #if not in the last 10 seconds, save to database and give feedback
                    else:
                        datetime_object = Datet.objects.create(name=user.username)
                        membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datet = datetime_object)
                        membership_object.save()
                        slowdown_object.save()

                        # send in slow button action to databse and render
                        questions = Question.objects.filter(lecture=group_name).values_list('questionText')
                        questions = list(reversed(questions))
                        form = QuestionForm()
                        return render_to_response('usersites/student.html', RequestContext(request, {'feedback':'feedback delivered',
                                                                                                     'form': form,
                                                                                                     'questions': questions}))

                else:   #user has not pressed button in this lecture before so we can simply save to database and continue
                    datetime_object = Datet.objects.create(name = user.username)
                    slowdown_object = Slowdown.objects.create(name=user.username)
                    membership_object = Membership.objects.create(group = group, person = user, slowdown = slowdown_object, datet = datetime_object)
                    membership_object.save()

                form = QuestionForm()
                questions = Question.objects.filter(lecture=group_name).values_list('questionText')
                questions = list(reversed(questions))
                return render_to_response('usersites/student.html', RequestContext(request, {'form': form, 'questions': questions}))
        elif request.POST['slowbtn'] == 'question' :
            form = QuestionForm(request.POST)
            if form.is_valid():
                Question.objects.create(questionText=form.cleaned_data['question'], lecture=group_name)

            questions = Question.objects.filter(lecture=group_name).values_list('questionText')
            questions = list(reversed(questions))
            form = QuestionForm()

            return render_to_response('usersites/student.html', RequestContext(request,
                                                                               {'form': form,
                                                                                'questions': questions}))

        else:   #group is not valid, redirect to /lecture page
            return HttpResponseRedirect('/lectures')
    else:   #load template
        form = QuestionForm()
        questions = Question.objects.filter(lecture=group_name).values_list('questionText')
        questions = list(reversed(questions))
        variables = RequestContext(request, {'form': form, 'questions': questions})
        return render_to_response('usersites/student.html', variables)

#view for the homepage, what you see after you have logged in
# -pass current username so that the user can feel welcome ~~
@login_required(login_url='login')
def homepage_view(request):
    variables = RequestContext(request, {'username':request.user.username})
    return render_to_response('homepage.html', variables)

#view for the teacher inside a lecture
@login_required(login_url='login')
def teacher_view(request):
    group_name = request.GET.get('lecture_name')    # get lecture name from url

    #check if the user is the owner, if not redirect to the lectures page
    if (request.user.user_permissions.filter(codename='owner_'+group_name).count() == 1):

        #check if anyone has pressed the slow down button, if not redirect to waiting page..
        if Membership.objects.filter(group = Group.objects.filter(name=group_name)[0]).count() > 0:
            membership_objects = Membership.objects.filter(group = Group.objects.filter(name=group_name)[0])    #find relations where the lecture is involved
            start_time = membership_objects[0].datet.datet                                                      #find the start time for graph purpose

            total_count = membership_objects.count()        #query that finds the total number of slowdown requests

            #query that finds the number of slowdown request the last minute, inefficiant but works..
            count_last_minute = 0
            for object in membership_objects:
                if (object.datet.datet) > timezone.now()-timedelta(minutes=1):
                    count_last_minute += 1

            #prepare a list for graph in template TODO: make it more dynamic, when end of lecture, restart graph
            data = pylist(range(0,total_count))

            minutelist = {}
            for feedback in data:
                key = round((membership_objects[feedback].datet.datet - start_time).total_seconds()/60%60)
                if key in minutelist:
                    minutelist[key] += 1
                else:
                    minutelist[key] = 1

            liste = [['Time', 'Slowdown pressed']]

            for i in range(0, 60, 2):
                count = 0
                if i in minutelist.keys():
                    count += minutelist[i]
                elif i - 1 in minutelist.keys():
                    count += minutelist[i - 1]
                liste.append([i, count])

            questions = Question.objects.filter(lecture=group_name).values_list('questionText')
            questions = list(reversed(questions))

            variables = RequestContext(request, {'count': count_last_minute, 'array':json.dumps(liste), 'start_time':start_time, 'questions': questions}) #Make variables readable for html

            return render_to_response('usersites/teacher.html', variables)
        else:
            return render_to_response('usersites/wait.html') # load the waiting page, no input from users yet
    else:
        return HttpResponseRedirect('/lectures')

#view for the user view
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

#view to handle users trying to join a lecture
# -Sends them to either student or teacher page, depending on permissions
@login_required(login_url='login')
def joined_lecture_view(request):
    #try exception if someone enters another lecture name in url to try and hack us lol
    try:
        (Group.objects.get(name=request.GET.get('lecture_name', '/')))                          #get lecture from url
        user = request.user
        group = Group.objects.get(name=request.GET.get('lecture_name', '/'))                    #find the group with the unique group name
        if (user.user_permissions.filter(codename='owner_'+group.name).count() == 1):           #check if the user is the owner, if owner, send to teacher page
            return HttpResponseRedirect('/usersites/teacher/?lecture_name=%s' % (group.name))
        else:                                                                                   #if user is not owner, send to studentpage
            return HttpResponseRedirect('/usersites/student/?lecture_name=%s' % (group.name))
    except:
        return HttpResponseRedirect('/lecture')
