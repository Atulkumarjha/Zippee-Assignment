import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestTaskCRUD:
    """Test basic CRUD operations on tasks."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password')

    @pytest.fixture
    def authenticated_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def task(self, user):
        return Task.objects.create(
            title='Sample Task',
            description='Sample Description',
            user=user
        )

    def test_create_task(self, authenticated_client, user):
        """Test creating a task."""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'New Task Description',
            'completed': False
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.count() == 1
        assert Task.objects.get().user == user
        assert Task.objects.get().title == 'New Task'

    def test_create_task_minimal(self, authenticated_client, user):
        """Test creating a task with only required field (title)."""
        url = reverse('task-list')
        data = {'title': 'Minimal Task'}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get()
        assert task.title == 'Minimal Task'
        assert task.description is None  # description field allows NULL
        assert task.completed is False

    def test_list_tasks(self, authenticated_client, user):
        """Test retrieving list of tasks."""
        Task.objects.create(title='Task 1', user=user)
        Task.objects.create(title='Task 2', user=user)
        url = reverse('task-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_retrieve_specific_task(self, authenticated_client, task):
        """Test retrieving a specific task."""
        url = reverse('task-detail', args=[task.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == task.title
        assert response.data['id'] == task.id

    def test_update_task(self, authenticated_client, task):
        """Test updating a task."""
        url = reverse('task-detail', args=[task.id])
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'completed': True
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Task'
        assert task.description == 'Updated Description'
        assert task.completed is True

    def test_partial_update_task(self, authenticated_client, task):
        """Test partial update (PATCH) of a task."""
        url = reverse('task-detail', args=[task.id])
        data = {'completed': True}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.completed is True
        assert task.title == 'Sample Task'  # unchanged

    def test_delete_task(self, authenticated_client, task):
        """Test deleting a task."""
        url = reverse('task-detail', args=[task.id])
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Task.objects.count() == 0

    def test_task_not_found(self, authenticated_client):
        """Test retrieving a non-existent task."""
        url = reverse('task-detail', args=[9999])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskPermissions:
    """Test permission and authorization on tasks."""
    
    @pytest.fixture
    def user1(self):
        return User.objects.create_user(email='user1@example.com', password='password')

    @pytest.fixture
    def user2(self):
        return User.objects.create_user(email='user2@example.com', password='password')

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_user(
            email='admin@example.com',
            password='password',
            is_staff=True,
            is_superuser=True
        )

    @pytest.fixture
    def task_user1(self, user1):
        return Task.objects.create(title='User1 Task', user=user1)

    def test_user_can_only_see_own_tasks(self, user1, user2):
        """Test that users can only see their own tasks."""
        task1 = Task.objects.create(title='User1 Task', user=user1)
        task2 = Task.objects.create(title='User2 Task', user=user2)

        client = APIClient()
        client.force_authenticate(user=user1)
        
        url = reverse('task-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == task1.id

    def test_user_cannot_access_other_user_task(self, user1, user2, task_user1):
        """Test that a user cannot access another user's task."""
        client = APIClient()
        client.force_authenticate(user=user2)
        
        url = reverse('task-detail', args=[task_user1.id])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_cannot_update_other_user_task(self, user1, user2, task_user1):
        """Test that a user cannot update another user's task."""
        client = APIClient()
        client.force_authenticate(user=user2)
        
        url = reverse('task-detail', args=[task_user1.id])
        data = {'title': 'Hacked Task'}
        response = client.put(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        task_user1.refresh_from_db()
        assert task_user1.title == 'User1 Task'

    def test_user_cannot_delete_other_user_task(self, user1, user2, task_user1):
        """Test that a user cannot delete another user's task."""
        client = APIClient()
        client.force_authenticate(user=user2)
        
        url = reverse('task-detail', args=[task_user1.id])
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.filter(id=task_user1.id).exists()

    def test_admin_can_see_all_tasks(self, admin_user, user1, user2):
        """Test that admin users can see all tasks."""
        task1 = Task.objects.create(title='User1 Task', user=user1)
        task2 = Task.objects.create(title='User2 Task', user=user2)

        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        url = reverse('task-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_admin_can_update_other_user_task(self, admin_user, user1, task_user1):
        """Test that admin can update other user's task."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        url = reverse('task-detail', args=[task_user1.id])
        data = {'title': 'Admin Updated Task', 'completed': True}
        response = client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        task_user1.refresh_from_db()
        assert task_user1.title == 'Admin Updated Task'

    def test_admin_can_delete_other_user_task(self, admin_user, user1, task_user1):
        """Test that admin can delete other user's task."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        url = reverse('task-detail', args=[task_user1.id])
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task_user1.id).exists()


@pytest.mark.django_db
class TestTaskAuthentication:
    """Test authentication requirements."""
    
    def test_unauthenticated_cannot_list_tasks(self):
        """Test that unauthenticated users cannot list tasks."""
        client = APIClient()
        url = reverse('task-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_create_task(self):
        """Test that unauthenticated users cannot create tasks."""
        client = APIClient()
        url = reverse('task-list')
        data = {'title': 'New Task'}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_update_task(self):
        """Test that unauthenticated users cannot update tasks."""
        user = User.objects.create_user(email='test@example.com', password='password')
        task = Task.objects.create(title='Task', user=user)
        
        client = APIClient()
        url = reverse('task-detail', args=[task.id])
        data = {'title': 'Updated'}
        response = client.put(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_delete_task(self):
        """Test that unauthenticated users cannot delete tasks."""
        user = User.objects.create_user(email='test@example.com', password='password')
        task = Task.objects.create(title='Task', user=user)
        
        client = APIClient()
        url = reverse('task-detail', args=[task.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTaskFiltering:
    """Test filtering and ordering of tasks."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password')

    @pytest.fixture
    def tasks(self, user):
        Task.objects.create(title='Completed Task 1', user=user, completed=True)
        Task.objects.create(title='Pending Task 1', user=user, completed=False)
        Task.objects.create(title='Completed Task 2', user=user, completed=True)
        Task.objects.create(title='Pending Task 2', user=user, completed=False)

    def test_filter_by_completed_status(self, user, tasks):
        """Test filtering tasks by completion status."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Filter completed
        url = reverse('task-list') + '?completed=true'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        for task in response.data['results']:
            assert task['completed'] is True

    def test_filter_by_pending_status(self, user, tasks):
        """Test filtering tasks by pending (incomplete) status."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Filter pending
        url = reverse('task-list') + '?completed=false'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        for task in response.data['results']:
            assert task['completed'] is False

    def test_order_by_created_at_descending(self, user, tasks):
        """Test ordering tasks by creation date (newest first)."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list') + '?ordering=-created_at'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        created_dates = [task['created_at'] for task in response.data['results']]
        assert created_dates == sorted(created_dates, reverse=True)

    def test_order_by_created_at_ascending(self, user, tasks):
        """Test ordering tasks by creation date (oldest first)."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list') + '?ordering=created_at'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        created_dates = [task['created_at'] for task in response.data['results']]
        assert created_dates == sorted(created_dates)


@pytest.mark.django_db
class TestTaskPagination:
    """Test pagination of task lists."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password')

    @pytest.fixture
    def many_tasks(self, user):
        # Create 25 tasks (default page size is 10)
        for i in range(25):
            Task.objects.create(title=f'Task {i+1}', user=user)

    def test_default_pagination(self, user, many_tasks):
        """Test default pagination (10 items per page)."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
        assert response.data['previous'] is None

    def test_pagination_next_page(self, user, many_tasks):
        """Test accessing the next page."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list') + '?page=2'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
        assert response.data['previous'] is not None

    def test_pagination_last_page(self, user, many_tasks):
        """Test accessing the last page."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list') + '?page=3'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['next'] is None
        assert response.data['previous'] is not None

    def test_invalid_page_number(self, user, many_tasks):
        """Test accessing an invalid page number."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list') + '?page=999'
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskValidation:
    """Test input validation and error handling."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password')

    def test_create_task_empty_title(self, user):
        """Test creating a task with empty title."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list')
        data = {'title': ''}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_task_missing_title(self, user):
        """Test creating a task without title."""
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-list')
        data = {'description': 'Task without title'}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_task_invalid_completed_value(self, user):
        """Test updating task with invalid completed value."""
        task = Task.objects.create(title='Task', user=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('task-detail', args=[task.id])
        data = {'title': 'Updated', 'completed': 'invalid'}
        response = client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
