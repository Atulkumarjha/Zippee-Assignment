import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_user_success(self):
        """Test successful user registration."""
        client = APIClient()
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpassword123'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        assert User.objects.get().email == 'newuser@example.com'

    def test_register_user_duplicate_email(self):
        """Test registering with duplicate email."""
        User.objects.create_user(email='test@example.com', password='password')
        
        client = APIClient()
        data = {
            'email': 'test@example.com',
            'password': 'strongpassword123'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.count() == 1

    def test_register_user_missing_email(self):
        """Test registration without email."""
        client = APIClient()
        data = {
            'password': 'strongpassword123'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_missing_password(self):
        """Test registration without password."""
        client = APIClient()
        data = {
            'email': 'test@example.com'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_invalid_email(self):
        """Test registration with invalid email format."""
        client = APIClient()
        data = {
            'email': 'not-an-email',
            'password': 'strongpassword123'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_empty_email(self):
        """Test registration with empty email."""
        client = APIClient()
        data = {
            'email': '',
            'password': 'strongpassword123'
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_empty_password(self):
        """Test registration with empty password."""
        client = APIClient()
        data = {
            'email': 'test@example.com',
            'password': ''
        }
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registered_user_can_login(self):
        """Test that registered user can login."""
        # Register
        client = APIClient()
        register_data = {
            'email': 'newuser@example.com',
            'password': 'strongpassword123'
        }
        register_url = reverse('register')
        register_response = client.post(register_url, register_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'strongpassword123'
        }
        login_url = reverse('token_obtain_pair')
        login_response = client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access' in login_response.data
        assert 'refresh' in login_response.data


@pytest.mark.django_db
class TestUserLogin:
    """Test user login and JWT token functionality."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password123')

    def test_login_user_success(self, user):
        """Test successful user login."""
        client = APIClient()
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_user_wrong_password(self, user):
        """Test login with wrong password."""
        client = APIClient()
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_user_nonexistent_email(self):
        """Test login with non-existent email."""
        client = APIClient()
        data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_email(self, user):
        """Test login without email."""
        client = APIClient()
        data = {
            'password': 'password123'
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_password(self, user):
        """Test login without password."""
        client = APIClient()
        data = {
            'email': 'test@example.com'
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_empty_credentials(self):
        """Test login with empty email and password."""
        client = APIClient()
        data = {
            'email': '',
            'password': ''
        }
        url = reverse('token_obtain_pair')
        response = client.post(url, data)
        # Empty credentials return 400 (validation error), not 401
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_access_token_is_valid(self, user):
        """Test that access token works for authenticated requests."""
        client = APIClient()
        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_url = reverse('token_obtain_pair')
        login_response = client.post(login_url, login_data)
        access_token = login_response.data['access']

        # Use access token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        tasks_url = reverse('task-list')
        tasks_response = client.get(tasks_url)
        assert tasks_response.status_code == status.HTTP_200_OK

    def test_invalid_access_token(self):
        """Test using invalid access token."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.here')
        url = reverse('task-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """Test JWT token refresh functionality."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password123')

    def test_refresh_token_success(self, user):
        """Test successful token refresh."""
        client = APIClient()
        # Login to get refresh token
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_url = reverse('token_obtain_pair')
        login_response = client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Refresh token
        refresh_data = {'refresh': refresh_token}
        refresh_url = reverse('token_refresh')
        refresh_response = client.post(refresh_url, refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token."""
        client = APIClient()
        refresh_data = {'refresh': 'invalid.token.here'}
        refresh_url = reverse('token_refresh')
        response = client.post(refresh_url, refresh_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_missing(self):
        """Test refresh without token."""
        client = APIClient()
        refresh_data = {}
        refresh_url = reverse('token_refresh')
        response = client.post(refresh_url, refresh_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_new_access_token_is_valid(self, user):
        """Test that new access token from refresh works."""
        client = APIClient()
        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_url = reverse('token_obtain_pair')
        login_response = client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Refresh to get new access token
        refresh_data = {'refresh': refresh_token}
        refresh_url = reverse('token_refresh')
        refresh_response = client.post(refresh_url, refresh_data)
        new_access_token = refresh_response.data['access']

        # Use new access token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        tasks_url = reverse('task-list')
        tasks_response = client.get(tasks_url)
        assert tasks_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation_with_email(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        assert user.email == 'test@example.com'
        assert user.is_active is True
        assert user.is_staff is False

    def test_user_password_hashing(self):
        """Test that passwords are hashed, not stored as plain text."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        assert user.password != 'password123'
        assert user.check_password('password123')

    def test_superuser_creation(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword'
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        assert str(user) == 'test@example.com'
