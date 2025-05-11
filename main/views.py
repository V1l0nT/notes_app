from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required

from .forms import NoteForm, SignUpForm
from .models import Note, Category

@login_required
def index(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', None)

    if request.user.is_superuser:
        notes = Note.objects.order_by('id')
        title = 'Главная страница сайта - все заметки'
    else:
        notes = Note.objects.filter(author=request.user).order_by('id')
        title = 'Мои заметки'

    if query:
        notes = notes.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    if category_id:
        notes = notes.filter(category_id=category_id)
        # Можно изменить заголовок, чтобы показать фильтр
        category = Category.objects.filter(id=category_id).first()
        if category:
            title = f'Заметки категории "{category.name}"'

    return render(request, 'main/index.html', {'title': title, 'notes': notes, 'query': query})

def about(request):
    return render(request, 'main/about.html')


@login_required
def create(request):
    error = ''
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            return redirect('home')
        else:
            error = 'Форма содержит ошибки'
    
    else:
        form = NoteForm()
    
    context = {
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # сразу логиним пользователя после регистрации
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def category_list(request):
    if request.user.is_superuser:
        categories = Category.objects.annotate(
            notes_count=Count('note')
        ).filter(notes_count__gt=0).order_by('name')
    else:
        categories = Category.objects.annotate(
            notes_count=Count('note', filter=Q(note__author=request.user))
        ).filter(notes_count__gt=0).order_by('name')

    return render(request, 'main/category_list.html', {'categories': categories})

@login_required
def category_notes(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.user.is_superuser:
        notes = Note.objects.filter(category=category).select_related('author').order_by('-updated_at')
    else:
        notes = Note.objects.filter(author=request.user, category=category).order_by('-updated_at')

    return render(request, 'main/category_notes.html', {'category': category, 'notes': notes})


def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    return render(request, 'main/note_detail.html', {'note': note})

@login_required
def note_edit(request, note_id):
    if request.user.is_superuser:
        note = get_object_or_404(Note, id=note_id)
    else:
        note = get_object_or_404(Note, id=note_id, author=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = NoteForm(instance=note)
    return render(request, 'main/note_edit.html', {'form': form, 'note': note})

@login_required
def note_delete(request, note_id):
    if request.user.is_superuser:
        note = get_object_or_404(Note, id=note_id)
    else:
        note = get_object_or_404(Note, id=note_id, author=request.user)

    if request.method == 'POST':
        note.delete()
        return redirect('home')
    return render(request, 'main/note_confirm_delete.html', {'note': note})
