from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import UserCreationForm, AuthenticationForm
from .models import Favorite
from .tokens import account_activation_token
from catalog import views as c
from catalog.models import Product


def signin(request):
    """
    Signin page.

    Redirects on "index" page after login (or if user already logged in);
    Renders signin page if not logged in, with error if invalid.

    """

    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        email = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        login(request, user)
        return redirect("index")

    else:
        form = AuthenticationForm()

    return render(request, "account/signin.html", {"form": form})


def signup(request):
    """
    Signup page.

    Redirects on "index" page if logged in (or after form validation);
    Renders signup page if not logged in, with error if invalid.

    """
    context = {}
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    email = form.cleaned_data["email"]
                    user.is_active = False
                    user.save()
                    current_site = get_current_site(request)
                    mail_subject = "Lien d'activation Pur Beurre"
                    message = render_to_string('account/activation_mail.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return HttpResponse('Veuillez confirmer votre adresse mail.')
            except IntegrityError:
                form.errors['ExistingMail']= (
                    "Un compte est déjà enregistré avec cette adresse mail."
                    +"Merci de vous connecter")
        else:
            return render(request, "account/signup.html", {"form": form})
    else:
        form = UserCreationForm()
        return render(request, "account/signup.html", {"form": form})
    context['form'] = form
    context['errors'] = form.errors.items()
    return render(request, "account/signup.html", context)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse("Vous pouvez désormais vous connecter.")
    else:
        return HttpResponse("Erreur lors de l'activation")

def my_account(request):
    """
    Account page.

    Redirects on "index" page if not logged in;
    Renders account page if logged in.

    """
    if request.user.is_authenticated:
        return render(request, "account/my_account.html")
    else:
        return redirect(request, "index", {"Error": "Not Logged In"})


def signout(request):
    """
    Logout page.

    Redirects on "index" page after logout;

    """
    if request.user.is_authenticated:
        logout(request)
        return redirect("index")


def save(request):
    """
    Save a product as one of user's favorites.

    Returns "209" if saved;
    Returns "500" else;

    """

    if request.user.is_authenticated:
        if request.method == "GET":
            product_id = request.GET["product"]
            product = get_object_or_404(Product, pk=product_id)
            user = get_object_or_404(User, pk=request.user.id)
            new_favorite = Favorite.objects.get_or_create(user=user, product=product)
            return HttpResponse("209")

    return HttpResponse("500")


def mail_save(request):
    """
    Save a mail to a User account

    Return "209" if saved;
    Return "500" else;

    """

    if request.user.is_authenticated:
        if request.method == "GET":
            mail = request.GET["email"]
            user = get_object_or_404(User, pk=request.user.id)
            user.email = mail
            user.save()
            return HttpResponse("209")
    return HttpResponse("500")


def my_favorites(request):
    """
    User's favorites page.

    Renders a favorite page (9 favorites by pasge) if logged in;
    Returns "500" else;

    """
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user.id)
        fav_list = []
        for each in favorites:
            fav_list.append(each.product)
        paginator = Paginator(fav_list, 9)
        page = request.GET.get("page")
        try:
            favorites_page = paginator.page(page)
        except PageNotAnInteger:
            favorites_page = paginator.page(1)
        except EmptyPage:
            favorites_page = paginator.page(paginator.num_pages)
        context = {"products": favorites_page, "paginate": True}
        return render(request, "account/my_favorites.html", context)
    else :
        return HttpResponse("500")


def delete(request):
    """
    Delete one of User's favorites Products.

    Returns "209" if Favorite deleted;
    Returns "500" else.

    """

    if request.user.is_authenticated:
        if request.method == "GET":
            product_id = request.GET["product"]
            product = get_object_or_404(Product, pk=product_id)
            user = get_object_or_404(User, pk=request.user.id)
            favorite = get_object_or_404(Favorite, user=user.id, product=product_id)
            if favorite is not None:
                favorite.delete()
            return HttpResponse("209")

    return HttpResponse("500")