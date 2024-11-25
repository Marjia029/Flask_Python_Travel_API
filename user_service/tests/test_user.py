import pytest
import os
import tempfile
from models.user import UserRole, UserDTO, UserRepository


class TestUserRole:
    def test_user_role_values(self):
        """Test that UserRole enum has correct values"""
        assert UserRole.ADMIN.value == "Admin"
        assert UserRole.USER.value == "User"


class TestUserDTO:
    @pytest.fixture
    def sample_user(self):
        return UserDTO(
            email="test@example.com",
            name="Test User",
            role=UserRole.USER,
            password_hash="hashed_password"
        )

    def test_user_dto_creation(self, sample_user):
        """Test UserDTO instance creation with correct attributes"""
        assert sample_user.email == "test@example.com"
        assert sample_user.name == "Test User"
        assert sample_user.role == UserRole.USER
        assert sample_user.password_hash == "hashed_password"

    def test_to_dict(self, sample_user):
        """Test to_dict method returns correct dictionary"""
        user_dict = sample_user.to_dict()
        assert user_dict == {
            'email': 'test@example.com',
            'name': 'Test User',
            'role': 'User'
        }

    def test_to_safe_dict(self, sample_user):
        """Test to_safe_dict method returns
        dictionary without sensitive information"""
        safe_dict = sample_user.to_safe_dict()
        assert safe_dict == {
            'name': 'Test User',
            'role': 'User'
        }
        assert 'email' not in safe_dict
        assert 'password_hash' not in safe_dict


class TestUserRepository:
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        fd, path = tempfile.mkstemp()
        yield path
        os.close(fd)
        os.unlink(path)

    @pytest.fixture
    def sample_repository(self, temp_file):
        """Create a repository instance with a temporary file"""
        return UserRepository(temp_file)

    @pytest.fixture
    def populated_repository(self, sample_repository):
        """Create a repository with some test users"""
        test_users = [
            UserDTO("user1@example.com", "User One", UserRole.USER, "hash1"),
            UserDTO("admin@example.com", "Admin User", UserRole.ADMIN, "hash2")
        ]
        for user in test_users:
            sample_repository.create_user(user)
        return sample_repository

    def test_repository_initialization(self, sample_repository):
        """Test repository initialization with empty file"""
        assert isinstance(sample_repository.users, dict)
        assert len(sample_repository.users) == 0

    def test_create_user(self, sample_repository):
        """Test creating a new user"""
        user = UserDTO("test@example.com", "Test User", UserRole.USER, "hash")
        sample_repository.create_user(user)
        assert len(sample_repository.users) == 1
        assert sample_repository.get_user("test@example.com") == user

    def test_create_duplicate_user(self, populated_repository):
        """Test creating a user with existing email raises ValueError"""
        duplicate_user = UserDTO(
            "user1@example.com",
            "Duplicate",
            UserRole.USER,
            "hash"
        )
        with pytest.raises(ValueError, match="User already exists"):
            populated_repository.create_user(duplicate_user)

    def test_get_user(self, populated_repository):
        """Test retrieving existing and non-existing users"""
        assert populated_repository.get_user("user1@example.com") is not None
        assert populated_repository.get_user("nonexistent@example.com") is None

    def test_get_all_users(self, populated_repository):
        """Test retrieving all users"""
        users = populated_repository.get_all_users()
        assert len(users) == 2
        assert any(user.email == "user1@example.com" for user in users)
        assert any(user.email == "admin@example.com" for user in users)

    def test_save_and_load_users(self, populated_repository, temp_file):
        """Test saving users to file and loading them back"""
        # Get initial users
        initial_users = populated_repository.get_all_users()

        # Create new repository instance with same file to test loading
        new_repository = UserRepository(temp_file)
        loaded_users = new_repository.get_all_users()

        # Compare users
        assert len(loaded_users) == len(initial_users)
        for user in loaded_users:
            assert user.email in [u.email for u in initial_users]
            assert user.name in [u.name for u in initial_users]
            assert user.role in [u.role for u in initial_users]
            assert user.password_hash in [
                u.password_hash for u in initial_users
            ]

    def test_save_users_with_invalid_path(self, temp_file):
        """Test saving users with invalid file path"""
        repository = UserRepository(temp_file)
        repository.file_path = "/invalid/path/users.py"

        with pytest.raises(Exception):
            repository.save_users()

    def test_load_users_with_invalid_content(self, temp_file):
        """Test loading users with invalid file content"""
        # Write invalid content to file
        with open(temp_file, 'w') as f:
            f.write("invalid content")

        repository = UserRepository(temp_file)
        assert len(repository.users) == 0
