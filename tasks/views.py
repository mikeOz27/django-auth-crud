from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required #decorador de funciones

# Create your views here.


def home(request):
    return render(request, 'home.html')

def signin(request):
    form = AuthenticationForm()
    if request.method == 'GET':
        # GET
        return render(request, 'signin.html', {'form': form})
    else:
        # login
        user = authenticate(
            request, username = request.POST['username'], 
            password = request.POST['password']
        )
        if user is None:
            return render(request, 'signin.html', {'form': form, 'error': 'Usuario y/o contraseña incorrecta'})
        else:
            login(request, user)
            return redirect('tasks')

def signup(request):
    form = UserCreationForm()
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': form})
    else:
        # POST
        if request.POST['password1'] == request.POST['password2']:
            try:
               # registro de usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'Usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': form,
            'error': 'La contraseña no coincide'
        })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'GET':  
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Los datos que ingresaste son incorrectos'
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm })
    else:
       try:
            form = TaskForm(request.POST)
            if form.is_valid():
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')
       except ValueError:
           return render(request, 'create_task.html', {
               'form': TaskForm,
               'error': 'Los datos que ingresaste son incorrectos'
           }) 
