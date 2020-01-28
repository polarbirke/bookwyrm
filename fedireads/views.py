''' application views/pages '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg, FilteredRelation, Q
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from fedireads import models, openlibrary
from fedireads import federation as api
from fedireads.settings import DOMAIN
import re

@login_required
def home(request):
    ''' user feed '''
    shelves = models.Shelf.objects.filter(user=request.user.id)
    recent_books = models.Book.objects.order_by(
        'added_date'
    ).annotate(
        user_shelves=FilteredRelation(
            'shelves',
            condition=Q(shelves__user_id=request.user.id)
        )
    ).values('id', 'authors', 'data', 'user_shelves', 'openlibrary_key')

    following = models.User.objects.filter(
        Q(followers=request.user) | Q(id=request.user.id))

    activities = models.Activity.objects.filter(
        user__in=following
    ).order_by('-created_date')[:10]

    data = {
        'user': request.user,
        'shelves': shelves,
        'recent_books': recent_books,
        'activities': activities,
    }
    return TemplateResponse(request, 'feed.html', data)


@csrf_exempt
def user_login(request):
    ''' authentication '''
    # send user to the login page
    if request.method == 'GET':
        return TemplateResponse(request, 'login.html')

    # authenticate user
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(request.GET.get('next', '/'))
    return TemplateResponse(request, 'login.html')


@csrf_exempt
@login_required
def user_logout(request):
    ''' done with this place! outa here! '''
    logout(request)
    return redirect('/')


@login_required
def user_profile(request, username):
    ''' profile page for a user '''
    user = models.User.objects.get(username=username)
    books = models.Book.objects.filter(shelves__user=user)
    data = {
        'user': user,
        'books': books,
        'is_self': request.user.id == user.id,
    }
    return TemplateResponse(request, 'user.html', data)


@login_required
def book_page(request, book_identifier):
    ''' info about a book '''
    book = openlibrary.get_or_create_book('/book/' + book_identifier)
    reviews = models.Review.objects.filter(
        Q(work=book.works.first()) | Q(book=book)
    )
    rating = reviews.aggregate(Avg('rating'))
    data = {
        'book': book,
        'reviews': reviews,
        'rating': rating['rating__avg'],
    }
    return TemplateResponse(request, 'book.html', data)


@csrf_exempt
@login_required
def shelve(request, shelf_id, book_id):
    ''' put a book on a user's shelf '''
    book = models.Book.objects.get(id=book_id)
    shelf = models.Shelf.objects.get(identifier=shelf_id)
    api.handle_shelve(request.user, book, shelf)
    return redirect('/')

@csrf_exempt
@login_required
def review(request):
    ''' create a book review note '''
    book_identifier = request.POST.get('book')
    book = openlibrary.get_or_create_book(book_identifier)
    name = request.POST.get('name')
    content = request.POST.get('content')
    rating = request.POST.get('rating')
    api.handle_review(request.user, book, name, content, rating)
    return redirect(book_identifier)


@csrf_exempt
@login_required
def follow(request):
    ''' follow another user, here or abroad '''
    to_follow = request.POST.get('user')
    to_follow = models.User.objects.get(id=to_follow)

    api.handle_outgoing_follow(request.user, to_follow)
    return redirect('/user/%s' % to_follow.username)


@csrf_exempt
@login_required
def unfollow(request):
    ''' unfollow a user '''
    followed = request.POST.get('user')
    followed = models.User.objects.get(id=followed)
    followed.followers.remove(request.user)
    return redirect('/user/%s' % followed.username)


@csrf_exempt
@login_required
def search(request):
    ''' that search bar up top '''
    query = request.GET.get('q')
    if re.match(r'\w+@\w+.\w+', query):
        results = [api.handle_account_search(query)]
    else:
        results = []

    return TemplateResponse(request, 'results.html', {'results': results})


def simplify_local_username(user):
    ''' helper for getting the short username for local users '''
    return user.username.replace('@%s' % DOMAIN, '')
