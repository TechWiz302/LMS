from django.contrib.auth.views import LoginView
from itertools import chain
from operator import attrgetter
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import IssueRequest, IssuedBook
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import IssuedBook, IssueRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import render, HttpResponse, redirect
import requests
import random
from urllib.parse import unquote
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.

def index(request):
    keyword_list = ["self-improvement", "mystery", "business", "Coding",
                    "travel", "Health and Wellness", "romance", "teen"]
    book_data_list = []

    for keyword in keyword_list:
        book_data = get_book_data(keyword)
        if book_data:
            book_data_list.append(book_data)

    context = {
        "book_data_list": book_data_list
    }
    return render(request, 'rsLib/index.html', context)


def get_book_data(keyword):
    url = f"https://www.googleapis.com/books/v1/volumes?q={keyword}&orderBy=newest&maxResults=40"
    response = requests.get(url)
    data = response.json()

    if "items" in data:
        items = data["items"]
        random.shuffle(items)
        for item in items:
            volume_info = item.get("volumeInfo", {})
            title = volume_info.get("title")
            volume_id = item.get("id")  # Get the volumeId

            image_links = volume_info.get("imageLinks", {})
            cover_image = image_links.get(
                "thumbnail") if "thumbnail" in image_links else None
            description = volume_info.get("description")
            editors = volume_info.get("publisher")
            authors = volume_info.get("authors")
            language = volume_info.get("language")

            if cover_image and description and editors and authors and language:
                return {
                    "title": title,
                    "volume_id": volume_id,  # Include the volumeId
                    "cover_image": cover_image,
                    "description": description,
                    "editors": editors,
                    "authors": authors,
                    "language": language
                }

    return None

def about(request):
    return render(request, 'rsLib/about.html')


def collection(request):
    return render(request, 'rsLib/collection.html')


def event(request):
    return render(request, 'rsLib/event.html')


def book_details(request, title, volume_id):
    decoded_title = unquote(title)

    response = requests.get(
        f"https://www.googleapis.com/books/v1/volumes/{volume_id}")
    data = response.json()

    if "volumeInfo" in data:
        volume_info = data["volumeInfo"]
        cover_image = volume_info.get("imageLinks", {}).get("thumbnail", "")
        description = volume_info.get("description", "")
        editors = volume_info.get("publisher", "")
        authors = ", ".join(volume_info.get("authors", []))
        language = volume_info.get("language", "")
        paper_back = volume_info.get("printType", "")

        context = {
            'title': decoded_title, 
            'cover_image': cover_image,
            'description': description,
            'editors': editors,
            'authors': authors,
            'language': language,
            'paper_back': paper_back,
            'volume_id': volume_id
        }

        return render(request, 'rsLib/book_details.html', context)

    return HttpResponse("Book details not found.")

@login_required
def issue_request(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        volume_id = request.POST.get('volume_id', '')

        if title and volume_id:
            issue_request = IssueRequest(
                title=title, volume_id=volume_id, user=request.user)
            issue_request.save()
            messages.success(
                request, 'Book issue request submitted successfully!  Contact or Meet your Librarian for further updates')
        else:
            messages.error(request, 'Missing title or volume_id.')

    return redirect('book_details', title=title, volume_id=volume_id)


@login_required
def issue_requests(request):
    issue_requests = IssueRequest.objects.all()
    total_requests = IssueRequest.objects.count()
    context = {
        'issue_requests': issue_requests,
        'total_requests': total_requests
    }
    return render(request, 'rsLib/issue_requests.html', context)


@login_required
def confirm_request(request, request_id):
    if request.method == 'POST':
        issue_request = get_object_or_404(IssueRequest, pk=request_id)
        if issue_request:
            issued_book = IssuedBook(
                title=issue_request.title, volume_id=issue_request.volume_id, user=issue_request.user, issued_at=timezone.now())
            issued_book.save()
            issue_request.delete()
            return HttpResponse('success')
        else:
            return HttpResponse('error')


@login_required
def delete_request(request, request_id):
    if request.method == 'POST':
        issue_request = get_object_or_404(IssueRequest, pk=request_id)
        if issue_request:
            issue_request.delete()
            return HttpResponse('success')
        else:
            return HttpResponse('error')


@login_required
def issued_books(request):
    issued_books = IssuedBook.objects.all()
    total_requests = IssuedBook.objects.count()
    context = {
        'issued_books': issued_books,
        'total_requests': total_requests
    }
    return render(request, 'rsLib/issued_books.html', context)


@login_required
def returned_book(request, request_id):
    if request.method == 'POST':
        return_book = get_object_or_404(IssuedBook, pk=request_id)
        if issue_request:
            return_book.delete()
            return HttpResponse('success')
        else:
            return HttpResponse('error')


def search_books(request):
    results = []
    if request.method == 'GET':
        search_query = request.GET.get('q', '').strip()
        if search_query:
            max_results_per_call = 10
            total_results_to_fetch = 40  

            for start_index in range(0, total_results_to_fetch, max_results_per_call):
                api_url = 'https://www.googleapis.com/books/v1/volumes?q={}&startIndex={}&maxResults={}'.format(
                    search_query, start_index, max_results_per_call
                )
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('items', [])

                    for book in books:
                        volume_info = book.get('volumeInfo', {})
                        if 'imageLinks' in volume_info and 'description' in volume_info:
                            results.append(book)

    return render(request, 'rsLib/search_book.html', {'results': results, 'search_query': search_query})


def signup(request):
    if request.method=='POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        
        if password != cpassword:
            error_message = "Your 'Password' and 'Confirm password' are not same"
            return render(request, 'rsLib/signup.html', {'error_message': error_message})
        else:
            my_user = User.objects.create_superuser(username, email, password)
            my_user.save()
            return redirect('login')
         
    return render(request, 'rsLib/signup.html')

# demo_users = {'demoUser': 'demo@123'}

# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             auth_login(request, user)
#             next_page = request.GET.get('next')
#             if next_page is not None:
#                 return redirect(next_page)
#             else:
#                 return redirect('home')
#         else:
#             error_message = "Invalid 'Username' or 'Password'. Please try again."
#             return render(request, 'rsLib/login.html', {'error_message': error_message})

#     return render(request, 'rsLib/login.html')

demo_users = {'demoUser': 'demo@123'}

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username in demo_users and demo_users[username] == password:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)

                next_page = request.GET.get('next')
                if next_page is not None:
                    return redirect(next_page)
                else:
                    return redirect('home')
        else:
            error_message = "Invalid 'Username' or 'Password'. Please try again."
            return render(request, 'rsLib/login.html', {'error_message': error_message})

    return render(request, 'rsLib/login.html')

def logout(request):
    auth_logout(request)
    request.session.clear() 
    return redirect('home')

@login_required
def dashboard(request):
    issue_requests = IssueRequest.objects.all()
    issued_books = IssuedBook.objects.all()
    users = User.objects.all()

    def get_timestamp(item):
        if isinstance(item, IssueRequest):
            return item.requested_at
        elif isinstance(item, IssuedBook):
            return item.issued_at

    combined_orders = sorted(
        chain(issue_requests, issued_books),
        key=get_timestamp,
        reverse=True
    )[:5]

    combined_orders_with_status = []
    for order in combined_orders:
        if isinstance(order, IssueRequest):
            combined_orders_with_status.append({'item': order, 'status': 'pending'})
        elif isinstance(order, IssuedBook):
            combined_orders_with_status.append({'item': order, 'status': 'completed'})

    context = {
        'recent_orders': combined_orders_with_status,
        'users': users,
    }

    return render(request, 'rsLib/admin.html', context)


@login_required
def show_users(request):
    users = User.objects.all()
    total_requests = User.objects.all().count()
    
    context = {
        'users': users, 
        'total_requests': total_requests
    }
    
    return render(request, 'rsLib/registered_user.html', context)


def adminSignup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        if User.objects.filter(username=username).exists():
            error_message = "The 'Username' you provided already exists!! Please try again. "
            return render(request, 'rsLib/adminSignUp.html', {'error_message': error_message})

        if password != cpassword:
            error_message = "Your 'Password' and 'Confirm password' are not same"
            return render(request, 'rsLib/adminSignUp.html', {'error_message': error_message})
        else:
            my_user = User.objects.create_superuser(username, email, password)
            my_user.save()
            return redirect('admin_login')

    return render(request, 'rsLib/adminSignUp.html')



def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            auth_login(request, user)
            next_page = request.GET.get('next')
            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect('dashboard')
        else:
            error_message = "Invalid 'Username' or 'Password'. Please try again."
            return render(request, 'rsLib/login.html', {'error_message': error_message})

    return render(request, 'rsLib/adminLogin.html')

def adminLogout(request):
    auth_logout(request)
    request.session.clear()
    return redirect('admin_login')

@login_required
def show_Adminusers(request):
    users = User.objects.all()
    total_requests = User.objects.all().count()
    
    context = {
        'users': users, 
        'total_requests': total_requests
    }
    
    return render(request, 'rsLib/adminTeam.html', context)


def get_timestamp(order):
    return getattr(order, 'issued_at', getattr(order, 'requested_at', None))


def recent_orders(request):
    issue_requests = IssueRequest.objects.all()
    issued_books = IssuedBook.objects.all()

    # Combine the querysets using itertools.chain
    combined_orders = sorted(
        chain(issue_requests, issued_books),
        key=get_timestamp,
        reverse=True
    )[:5]

    return render(request, 'rsLib/recent_orders.html', {'recent_orders': combined_orders})