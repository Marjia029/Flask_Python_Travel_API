import pytest
import os
import tempfile
import logging
from typing import Dict
from models.user import UserDTO, UserRole
from repositories.user_repository import UserRepository

class TestUserRepository:
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        fd, path = tempfile.mkstemp()
        yield path
        os.close(fd)
        os.unlink(path)

    @pytest.fixture
    def sample_user_data(self) -> Dict:
        """Sample user data for testing"""
        return {
            'test@example.com': {
                'name': 'Test User',
                'password': 'hashed_password_1',
                'role': 'User'
            },
            'admin@example.com': {
                'name': 'Admin User',
                'password': 'hashed_password_2',
                'role': 'Admin'
            }
        }

    @pytest.fixture
    def populated_file(self, temp_file, sample_user_data):
        """Create a temporary file with sample user data"""
        with open(temp_file, 'w') as f:
            f.write(f"users = {repr(sample_user_data)}")
        return temp_file

    @pytest.fixture
    def empty_repository(self, temp_file):
        """Create an empty repository"""
        return UserRepository(temp_file)

    @pytest.fixture
    def populated_repository(self, populated_file):
        """Create a repository with sample data"""
        return UserRepository(populated_file)

    def test_init_with_nonexistent_file(self, temp_file):
        """Test repository initialization with non-existent file"""
        non_existent_path = temp_file + "_nonexistent"
        repo = UserRepository(non_existent_path)
        assert isinstance(repo.users, dict)
        assert len(repo.users) == 0

    def test_init_with_existing_file(self, populated_repository, sample_user_data):
        """Test repository initialization with existing file"""
        assert len(populated_repository.users) == len(sample_user_data)
        
        # Check if users are loaded correctly
        test_user = populated_repository.get_user('test@example.com')
        assert test_user is not None
        assert test_user.name == 'Test User'
        assert test_user.role == UserRole.USER
        assert test_user.password_hash == 'hashed_password_1'

        admin_user = populated_repository.get_user('admin@example.com')
        assert admin_user is not None
        assert admin_user.name == 'Admin User'
        assert admin_user.role == UserRole.ADMIN
        assert admin_user.password_hash == 'hashed_password_2'

    def test_init_with_corrupted_file(self, temp_file):
        """Test repository initialization with corrupted file"""
        with open(temp_file, 'w') as f:
            f.write("This is not a valid Python dictionary")
        
        repo = UserRepository(temp_file)
        assert len(repo.users) == 0

    def test_save_users(self, empty_repository):
        """Test saving users to file"""
        user = UserDTO(
            email="new@example.com",
            name="New User",
            role=UserRole.USER,
            password_hash="hashed_password"
        )
        empty_repository.create_user(user)

        # Create new repository instance to test if data was saved
        new_repo = UserRepository(empty_repository.file_path)
        saved_user = new_repo.get_user("new@example.com")
        
        assert saved_user is not None
        assert saved_user.name == user.name
        assert saved_user.role == user.role
        assert saved_user.password_hash == user.password_hash

    def test_save_users_with_permission_error(self, empty_repository):
        """Test saving users with insufficient permissions"""
        empty_repository.file_path = "/root/test_users.py"  # A path that requires root access
        
        user = UserDTO(
            email="test@example.com",
            name="Test User",
            role=UserRole.USER,
            password_hash="hash"
        )
        
        with pytest.raises(Exception):
            empty_repository.create_user(user)

    def test_get_user_existing(self, populated_repository):
        """Test retrieving an existing user"""
        user = populated_repository.get_user("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == UserRole.USER

    def test_get_user_nonexistent(self, populated_repository):
        """Test retrieving a non-existent user"""
        user = populated_repository.get_user("nonexistent@example.com")
        assert user is None

    def test_create_user(self, empty_repository):
        """Test creating a new user"""
        user = UserDTO(
            email="new@example.com",
            name="New User",
            role=UserRole.USER,
            password_hash="hash"
        )
        
        empty_repository.create_user(user)
        assert len(empty_repository.users) == 1
        assert empty_repository.get_user("new@example.com") == user

    def test_create_duplicate_user(self, populated_repository):
        """Test creating a user with duplicate email"""
        duplicate_user = UserDTO(
            email="test@example.com",  # This email already exists
            name="Duplicate User",
            role=UserRole.USER,
            password_hash="hash"
        )
        
        with pytest.raises(ValueError, match="User already exists"):
            populated_repository.create_user(duplicate_user)

    def test_get_all_users(self, populated_repository, sample_user_data):
        """Test retrieving all users"""
        users = populated_repository.get_all_users()
        assert len(users) == len(sample_user_data)
        
        emails = [user.email for user in users]
        assert all(email in emails for email in sample_user_data.keys())

    @pytest.mark.parametrize("invalid_content", [
        "users = invalid_python_syntax",
        "users = None",
        "different_variable = {}",
        "",
        "users = {'invalid_email': {'missing': 'required_fields'}}"
    ])
    def test_load_users_with_invalid_content(self, temp_file, invalid_content):
        """Test loading users with various invalid file contents"""
        with open(temp_file, 'w') as f:
            f.write(invalid_content)
        
        repo = UserRepository(temp_file)
        assert len(repo.users) == 0

    def test_logging(self, caplog, populated_file):
        """Test if proper logging messages are generated"""
        with caplog.at_level(logging.INFO):
            repo = UserRepository(populated_file)
            assert "Successfully loaded 2 users" in caplog.text

            # Test logging for successful save
            user = UserDTO("new@example.com", "New User", UserRole.USER, "hash")
            repo.create_user(user)
            assert "Users saved successfully" in caplog.text

        # Test logging for errors
        with caplog.at_level(logging.ERROR):
            repo.file_path = "/root/test_users.py"  # This should cause a permission error
            with pytest.raises(Exception):
                repo.save_users()
            assert "Error saving users:" in caplog.text