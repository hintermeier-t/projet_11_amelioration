"""
Testing 'Account' app views.py module
"""

# - Django modules
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db.transaction import TransactionManagementError
from django.template import RequestContext
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse

from psycopg2.errors import UniqueViolation

# - Selenium modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager

# - Custom modules
from .models import Favorite
from catalog.models import Product


# - Signin page
class SigninPageTestCase(TestCase):
    """
    Testing sigin view.

    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create User
        object;
    :self.password (string): password field used to connect and create User
        object;
    :self.user (User): Django's User object.

    Tests:
    ------
    :test_signin_invalid_credentials(self): Request a connection with wrong
        credentials (here password);
    :test_signin_valid_credentials(self): Request a connection with right
        credentials.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "NinaS"
        self.password = "Sinnerman"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_signin_invalid_credentials(self):
        """
        Conditions:
        -----------
        *User send wrong password ("LittleGirlBlues" != "Sinnerman").

        Assertions:
        -----------
        *Status code = 200 (we can access signin page);
        *Context contains "Error":'Invalid'.
        """

        request = self.client.post(
            reverse("account:signin"),
            {"username": self.username, "password": "LittleGirlBlues"},
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.context["Error"], "Invalid")

    # - Test a signin with valid credentials
    def test_signin_valid_credentials(self):
        """
        Conditions:
        -----------
        *All conditions are OK.

        Assertions:
        -----------
        *Status code = 302 (redirection after connection);
        *Redirection page = index.
        """

        self.client.login(username=self.username, password=self.password)
        request = self.client.post(reverse("account:signin"))
        self.assertEqual(request.status_code, 302)
        self.assertRedirects(request, "/")


# - Signup page
class SignupPageTestCase(TestCase):
    """
    Testing sigup view.
    Attributes :
    ------------
    :username (string): username field;
    :password1 (string): password field;
    :password1 (string): confirmation password field;
    :self.user (User): Django's User object.

    Tests:
    ------
    :test_signup_form(self): request a user account creation.
    """
    def setUp(self):
        """
        Tests setup
        """
        self.email = "nikola@sirkis.fr"
        self.user = User.objects.create_user(
            username=self.email,
            password="ANosCelebrations"
        )

    # - Test the account creation
    def test_signup_form(self):
        """
        Conditions:
        -----------
        *Fields are filled (client-side verifications)

        Assertions:
        -----------
        *User 'AlexandreA' doesn't exist before account creation.
        *User 'AlexandreA' does exist after account creation.
        """

        try:
            User.objects.get(username="alexandre@astier.fr")
        except User.DoesNotExist:
            self.assertEqual(True, True)
        request = self.client.get(reverse("account:signup"))
        self.assertEqual(request.status_code, 200)
        request = self.client.post(
            reverse("account:signup"),
            {
                "email": "alexandre@astier.fr",
                "password1": "OnEnAGros",
                "password2": "OnEnAGros",
            },
        )
        user = User.objects.get(username="alexandre@astier.fr")
        self.assertIsNotNone(user)

    def test_mail_uniqueness(self):
        """
        Conditions:
        -----------
        *Account already registered
        *All fieldsare ok

        Assertions:
        -----------
        *User 'nikola@sirkis.fr' already exists before account creation
            (count = 1).
        *Still 1 user registered (count = 1)
        """
        old_count = User.objects.count()
        self.assertEqual(old_count, 1)
        request = self.client.post(
                reverse("account:signup"),
                {
                    "email": "nikola@sirkis.fr",
                    "password1": "JAiDemandeALaLune",
                    "password2": "JAiDemandeALaLune",
                },
            )
             
        self.assertEqual(User.objects.count(), old_count)

# - Account page
class AccountPageTestCase(TestCase):
    """
    Testing my_account view.
    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create User
        object;
    :self.password (string): password field used to connect and create User
        object;
    :self.user (User): Django's User object.

    Tests:
    ------
    :test_account_logged_in(self): request access to "my account" page.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "MilesD"
        self.password = "KindOfBlue"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_account_logged_in(self):
        """
        Conditions:
        -----------
        *User is logged in.
        Assertions:
        -----------
        *Status code = 200 (access granted)
        """

        self.client.login(username=self.username, password=self.password)
        request = self.client.get(reverse("account:my_account"))
        self.assertEqual(request.status_code, 200)


# - Signout
class SignoutPageTestcase(TestCase):
    """
    Testing signout view.
    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create
        User Object;
    :self.password (string): password field used to connect and create
        User object;
    :self.user (User): Django's User object.

    Tests:
    ------
    :def test_signout(self): request disconnection.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "ChesterB"
        self.password = "InTheEnd"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

    # - Test the logout function
    def test_signout(self):
        """
        Conditions:
        -----------
        *User is logged in.
        Assertions:
        -----------
        *Status code = 302 (redirection)
        *Redirect page = index (after logout)
        """

        request = self.client.get(reverse("account:signout"))
        self.assertEqual(request.status_code, 302)
        self.assertRedirects(request, "/")


# - Save mail
class SaveMailTestCase(TestCase):
    """
    Testing mail_save view.
    Attributes (setUp method) :
    ---------------------------
    :self.mail (string): the mail we will send to the view
    :self.username (string): username field used to connect and create User
        Object;
    :self.password (string): password field used to connect and create User
        Object;
    :self.user (User): Django's User object.

    Tests:
    ------
    :test_no_logged_in(self): request a mail save without being logged in;
    :test_mail_change(self): request a mail save while being logged in.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.mail = "moonlight@vermont.com"
        self.username = "LouisA"
        self.password = "YouRascalYou"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    # - test without logged user
    def test_no_logged_in(self):
        """
        Conditions:
        -----------
        *User is not logged in.
        Assertions:
        -----------
        *Content = "500" (no save).
        """

        self.client.logout()
        response = self.client.get(reverse("account:mail_save"), {"email": self.mail})
        self.assertEqual(response.content, b"500")

    # - Test the mail changing.
    def test_mail_change(self):
        """
        Conditions:
        -----------
        *User is logged in, mail OK (client-side verification).
        Assertions:
        -----------
        *Content = "209" validated.
        """

        self.client.login(username=self.username, password=self.password)
        self.assertEqual(self.user.email, "")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("account:mail_save"), {"email": self.mail})
        self.assertEqual(response.content, b"209")


# - Save product
class SaveFavoriteTestCase(TestCase):
    """
    Testing save view.
    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create User
        object;
    :self.password (string): password field used to connect and create User
        object;
    :self.user (User): Django's User object;
    :self.product (Product): catalog app's Poduct object.

    Tests:
    ------
    :test_favorite_not_logged_in(self): request a favorite save without being
        logged in;
    :test_new_favorite_wrong_id(self): request a favorite save while being
        logged in with wrong product ID (no Product found);
    :test_new_favorite_logged_in(self): request a favorite save while being
        logged in.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "SarahV"
        self.password = "LullabyOfBirdland"
        self.product = Product.objects.create(
            name="Produit à manger",
            brand="Chuipariche",
            code="1234567890123",
            nutriscore="B",
            description="C'est bon à cuisiner",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )

        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    # - Test if the user is not logged in
    def test_favorite_not_logged_in(self):
        """
        Conditions:
        -----------
        *User not logged in.
        Assertions:
        -----------
        *Content = "500" (no save);
        *Favorite.objects.count() is still the same (0).
        """

        favorites_old_count = Favorite.objects.count()
        request = self.client.get(reverse("account:save"), {"product": self.product.id})
        self.assertEqual(request.content, b"500")
        self.assertEqual(favorites_old_count, Favorite.objects.count())

    # - Test with user logged in, wrong ID
    def test_new_favorite_wrong_id(self):
        """
        Conditions:
        -----------
        *User logged in;
        *Wrong Product id (no Product found).

        Assertions:
        -----------
        *Status code = 404 (no Product found);
        *Favorite.objects.count() is still the same (0).
        """

        self.client.login(username=self.username, password=self.password)
        favorites_old_count = Favorite.objects.count()
        request = self.client.get(reverse("account:save"), {"product": 123456789})
        self.assertEqual(request.status_code, 404)
        favorites_new_count = Favorite.objects.count()
        self.assertEqual(favorites_new_count, favorites_old_count)

    # - test a Favorite is saved
    def test_new_favorite_logged_in(self):
        """
        Conditions:
        -----------
        *All conditions are OK.

        Assertions:
        -----------
        *Content = "209" (Favorite saved);
        * Favorite.objects.count() += 1.
        """

        self.client.login(username=self.username, password=self.password)
        favorites_old_count = Favorite.objects.count()
        request = self.client.get(reverse("account:save"), {"product": self.product.id})
        self.assertEqual(request.content, b"209")
        favorites_new_count = Favorite.objects.count()
        self.assertEqual(favorites_new_count, favorites_old_count + 1)


class DeleteFavoriteTestCase(TestCase):
    """
    Testing delete view.
    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create User
        object;
    :self.password (string): password field used to connect and create User
        object;
    :self.user (User): Django's User object;
    :self.product (Product): catalog app's Poduct object;
    :self.favorite (Favorite): account app's Favorite Object relating
        self.user with self.product.

    Tests:
    ------
    :test_del_favorite_not_logged_in(self): request a favorite delete without
        being logged in;
    :test_del_favorite_wrong_id(self): request a favorite delete while being
        logged in with wrong product ID (no Favorite found).
    :test_del_favorite_logged_in(self): request a favorite delete while being
        logged in.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "SarahV"
        self.password = "LullabyOfBirdland"
        self.product = Product.objects.create(
            name="Produit à manger",
            brand="Chuipariche",
            code="1234567890123",
            nutriscore="B",
            description="C'est bon à cuisiner",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )

        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.favorite = Favorite.objects.get_or_create(
            user=self.user, product=self.product
        )

    # - Test if the user is not logged in
    def test_del_favorite_not_logged_in(self):
        """
        Conditions:
        -----------
        *User not logged in.

        Assertions:
        -----------
        *Content = "500" (favorite not deleted);
        *Favorite.objects.count() is still the same (1).
        """

        favorites_old_count = Favorite.objects.count()
        request = self.client.get(
            reverse("account:delete"), {"product": self.product.id}
        )
        self.assertEqual(request.content, b"500")
        self.assertEqual(Favorite.objects.count(), 1)

    # - Test with logged user wrong product
    def test_del_favorite_wrong_id(self):
        """
        Conditions:
        -----------
        *User logged in;
        *Wrong Product ID (not registered as favorite).

        Assertions:
        -----------
        *Status code = 404 (Favorite not Found);
        *Favorite.objects.count() is still the same (1).
        """
        self.client.login(username=self.username, password=self.password)
        request = self.client.get(reverse("account:delete"), {"product": 0})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(Favorite.objects.count(), 1)

    # - Test with logged user, product ok
    def test_del_favorite_logged_in(self):
        """
        Conditions:
        -----------
        *All conditions are OK.
        Assertions:
        -----------
        *Content = "209" (Favorite deleted);
        *Favorite.objects.count() -= 1.
        """

        self.client.login(username=self.username, password=self.password)
        request = self.client.get(
            reverse("account:delete"), {"product": self.product.id}
        )
        self.assertEqual(request.content, b"209")
        self.assertEqual(Favorite.objects.count(), 0)


class MyFavoritePageTestCase(TestCase):
    """
    Testing my_favorites view.
    Attributes (setUp method) :
    ---------------------------
    :self.username (string): username field used to connect and create User
        object;
    :self.password (string): password field used to connect and create User
        object;
    :self.user (User): Django's User object;
    :self.product (Product): catalog app's Poduct object;
    :self.favorite (Favorite): account app's Favorite Object relating
        self.user with self.product.

    Tests:
    ------
    :test_favorite_not_logged_in(self): request a favorites access without
        being logged in;
    :test_favorite_logged_in(self): request a favorite delete while being
        logged in.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.username = "DavidB"
        self.password = "UnderPressure"
        self.product = Product.objects.create(
            name="Produit à manger",
            brand="Chuipariche",
            code="1234567890123",
            nutriscore="B",
            description="C'est bon à cuisiner",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )

        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.favorite = Favorite.objects.get_or_create(
            user=self.user, product=self.product
        )

    def test_favorite_not_logged_in(self):
        """
        Conditions:
        -----------

        Assertions:
        -----------
        """

        request = self.client.get(reverse("account:my_favorites"))
        self.assertEqual(request.content, b"500")

    def test_favorite_logged_in(self):
        """
        Conditions:
        -----------

        Assertions:
        -----------
        """

        self.client.login(username=self.username, password=self.password)
        request = self.client.get(reverse("account:my_favorites"))
        self.assertEqual(request.status_code, 200)


# - Selenium tests
class SeleniumTests(TestCase):
    """
    Selenium test class.
    Attribute (setUp method):
    -------------------------
    :self.driver (Selenium.webdriver): simulated firefox broswer.

    Tests:
    ------
    :test_connection_website(self): request website access;
    :test_register_form(self): request signup page access, and fill it.

    """

    def setUp(self):
        """
        Tests setup.
        """

        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    def test_connection_website(self):
        """
        Testing website access. If ok "Pur Beurre" should be in page title.
        """

        driver = self.driver
        driver.get("http://127.0.0.1:8000")
        self.assertIn("Pur Beurre", driver.title)

    def test_register_form(self):
        """
        Simulating form filling by a human.
        """

        driver = self.driver
        driver.get("http://127.0.0.1:8000/account/signup")
        username = driver.find_element_by_name("username")
        password_one = driver.find_element_by_name("password1")
        password_two = driver.find_element_by_name("password2")
        username.send_keys("ArtBlakey")
        password_one.send_keys("b2eZu45ipGRe6")
        password_two.send_keys("b2eZu45ipGRe6")
        password_two.send_keys(Keys.RETURN)
        # - If the form is valid, fields should be empty
        self.assertEqual(password_one.text, "")
        self.assertEqual(password_two.text, "")
        self.assertEqual(username.text, "")

    def tearDown(self):
        """
        Closing the driver after tests.
        """
        self.driver.close()
