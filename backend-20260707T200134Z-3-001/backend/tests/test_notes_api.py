import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, init_db, clear_notes, clear_users, hash_password


class SecureNotesApiTests(unittest.TestCase):
    """Comprehensive test suite for Secure Notes API"""

    def setUp(self):
        """Set up test client and database"""
        self.client = app.test_client()
        app.config['TESTING'] = True
        init_db()
        clear_notes()
        clear_users()
        
        # Test users
        self.user1_email = 'user1@example.com'
        self.user1_password = 'SecurePass123!'
        self.admin_email = 'admin@example.com'
        self.admin_password = 'AdminPass123!'

    def tearDown(self):
        """Clean up after tests"""
        clear_notes()
        clear_users()

    # ======================== AUTHENTICATION TESTS ========================

    def test_register_new_user_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['email'], self.user1_email)
        self.assertEqual(payload['data']['role'], 'user')
        self.assertIn('access_token', payload['data'])
        self.assertIn('refresh_token', payload['data'])

    def test_register_duplicate_email_fails(self):
        """Test that registering with duplicate email fails"""
        # First registration
        self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        
        # Second registration with same email
        response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': 'AnotherPass123!'
        })
        self.assertEqual(response.status_code, 409)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertEqual(payload['error']['code'], 'DUPLICATE_EMAIL')

    def test_register_invalid_email_fails(self):
        """Test that invalid email format fails"""
        response = self.client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'password': self.user1_password
        })
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertEqual(payload['error']['code'], 'VALIDATION_ERROR')

    def test_register_weak_password_fails(self):
        """Test that weak password fails validation"""
        weak_passwords = [
            'short',  # Too short
            'nouppercase123!',  # No uppercase
            'NOLOWERCASE123!',  # No lowercase
            'NoDigits!',  # No digits
            'NoSpecial123',  # No special characters
        ]
        
        for password in weak_passwords:
            response = self.client.post('/api/auth/register', json={
                'email': f'test{weak_passwords.index(password)}@example.com',
                'password': password
            })
            self.assertEqual(response.status_code, 400)
            payload = response.get_json()
            self.assertFalse(payload['success'])

    def test_register_missing_fields_fails(self):
        """Test that missing email or password fails"""
        # Missing email
        response = self.client.post('/api/auth/register', json={
            'password': self.user1_password
        })
        self.assertEqual(response.status_code, 400)
        
        # Missing password
        response = self.client.post('/api/auth/register', json={
            'email': self.user1_email
        })
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        """Test successful login"""
        # Register user first
        self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        
        # Login
        response = self.client.post('/api/auth/login', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertIn('access_token', payload['data'])
        self.assertIn('refresh_token', payload['data'])

    def test_login_invalid_credentials_fails(self):
        """Test that login with invalid credentials fails"""
        # Register user
        self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        
        # Try login with wrong password
        response = self.client.post('/api/auth/login', json={
            'email': self.user1_email,
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertEqual(payload['error']['code'], 'INVALID_CREDENTIALS')

    def test_login_nonexistent_user_fails(self):
        """Test that login with non-existent user fails"""
        response = self.client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': self.user1_password
        })
        self.assertEqual(response.status_code, 401)

    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # Register and login
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        refresh_token = reg_response.get_json()['data']['refresh_token']
        
        # Refresh token
        response = self.client.post('/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertIn('access_token', payload['data'])

    def test_logout_success(self):
        """Test successful logout"""
        # Register and login
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        access_token = reg_response.get_json()['data']['access_token']
        
        # Logout
        response = self.client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)

    # ======================== NOTES ENDPOINTS TESTS ========================

    def test_create_note_authenticated(self):
        """Test creating a note when authenticated"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        
        # Create note
        response = self.client.post('/api/notes', json={
            'title': 'Mi primera nota',
            'content': 'Contenido importante',
            'createdAt': 1710000000000
        }, headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['title'], 'Mi primera nota')

    def test_create_note_unauthenticated_fails(self):
        """Test that creating note without authentication fails"""
        response = self.client.post('/api/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        self.assertEqual(response.status_code, 401)

    def test_create_note_invalid_token_fails(self):
        """Test that creating note with invalid token fails"""
        response = self.client.post('/api/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        }, headers={'Authorization': 'Bearer invalid-token'})
        self.assertEqual(response.status_code, 422)

    def test_create_note_duplicate_title_fails(self):
        """Test that duplicate note titles fail for same user"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create first note
        self.client.post('/api/notes', json={
            'title': 'Unique Title',
            'content': 'First content'
        }, headers=headers)
        
        # Try to create note with same title
        response = self.client.post('/api/notes', json={
            'title': 'Unique Title',
            'content': 'Second content'
        }, headers=headers)
        
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()['error']['code'], 'DUPLICATE_TITLE')

    def test_list_notes_returns_only_user_notes(self):
        """Test that users only see their own notes"""
        # Register two users
        user1_response = self.client.post('/api/auth/register', json={
            'email': 'user1@test.com',
            'password': 'Pass123!User'
        })
        user1_token = user1_response.get_json()['data']['access_token']
        
        user2_response = self.client.post('/api/auth/register', json={
            'email': 'user2@test.com',
            'password': 'Pass123!User'
        })
        user2_token = user2_response.get_json()['data']['access_token']
        
        # User1 creates note
        self.client.post('/api/notes', json={
            'title': 'User1 Note',
            'content': 'User1 content'
        }, headers={'Authorization': f'Bearer {user1_token}'})
        
        # User2 creates note
        self.client.post('/api/notes', json={
            'title': 'User2 Note',
            'content': 'User2 content'
        }, headers={'Authorization': f'Bearer {user2_token}'})
        
        # User1 lists notes - should only see their own
        response = self.client.get('/api/notes',
            headers={'Authorization': f'Bearer {user1_token}'})
        payload = response.get_json()
        self.assertEqual(len(payload['data']), 1)
        self.assertEqual(payload['data'][0]['title'], 'User1 Note')

    def test_get_note_success(self):
        """Test getting a specific note"""
        # Register and create note
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        
        create_response = self.client.post('/api/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        }, headers={'Authorization': f'Bearer {token}'})
        note_id = create_response.get_json()['data']['id']
        
        # Get note
        response = self.client.get(f'/api/notes/{note_id}',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['title'], 'Test Note')

    def test_get_note_not_found_fails(self):
        """Test getting non-existent note fails"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        
        # Try to get non-existent note
        response = self.client.get('/api/notes/9999',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 404)

    def test_get_other_user_note_fails(self):
        """Test that user cannot access other user's notes"""
        # Register two users
        user1_response = self.client.post('/api/auth/register', json={
            'email': 'user1@test.com',
            'password': 'Pass123!User'
        })
        user1_token = user1_response.get_json()['data']['access_token']
        
        user2_response = self.client.post('/api/auth/register', json={
            'email': 'user2@test.com',
            'password': 'Pass123!User'
        })
        user2_token = user2_response.get_json()['data']['access_token']
        
        # User1 creates note
        create_response = self.client.post('/api/notes', json={
            'title': 'User1 Note',
            'content': 'User1 content'
        }, headers={'Authorization': f'Bearer {user1_token}'})
        note_id = create_response.get_json()['data']['id']
        
        # User2 tries to access User1's note
        response = self.client.get(f'/api/notes/{note_id}',
            headers={'Authorization': f'Bearer {user2_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['error']['code'], 'FORBIDDEN')

    def test_update_note_success(self):
        """Test updating a note"""
        # Register and create note
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        
        create_response = self.client.post('/api/notes', json={
            'title': 'Original Title',
            'content': 'Original content'
        }, headers={'Authorization': f'Bearer {token}'})
        note_id = create_response.get_json()['data']['id']
        
        # Update note
        response = self.client.put(f'/api/notes/{note_id}', json={
            'title': 'Updated Title',
            'content': 'Updated content'
        }, headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['title'], 'Updated Title')

    def test_delete_note_success(self):
        """Test deleting a note"""
        # Register and create note
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        
        create_response = self.client.post('/api/notes', json={
            'title': 'To Delete',
            'content': 'Delete me'
        }, headers={'Authorization': f'Bearer {token}'})
        note_id = create_response.get_json()['data']['id']
        
        # Delete note
        response = self.client.delete(f'/api/notes/{note_id}',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        get_response = self.client.get(f'/api/notes/{note_id}',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(get_response.status_code, 404)

    def test_delete_other_user_note_fails(self):
        """Test that user cannot delete other user's notes"""
        # Register two users
        user1_response = self.client.post('/api/auth/register', json={
            'email': 'user1@test.com',
            'password': 'Pass123!User'
        })
        user1_token = user1_response.get_json()['data']['access_token']
        
        user2_response = self.client.post('/api/auth/register', json={
            'email': 'user2@test.com',
            'password': 'Pass123!User'
        })
        user2_token = user2_response.get_json()['data']['access_token']
        
        # User1 creates note
        create_response = self.client.post('/api/notes', json={
            'title': 'User1 Note',
            'content': 'User1 content'
        }, headers={'Authorization': f'Bearer {user1_token}'})
        note_id = create_response.get_json()['data']['id']
        
        # User2 tries to delete User1's note
        response = self.client.delete(f'/api/notes/{note_id}',
            headers={'Authorization': f'Bearer {user2_token}'})
        self.assertEqual(response.status_code, 403)

    # ======================== VALIDATION TESTS ========================

    def test_note_title_length_validation(self):
        """Test title length validation"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Title too short
        response = self.client.post('/api/notes', json={
            'title': 'ab',
            'content': 'Valid content'
        }, headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # Title too long
        response = self.client.post('/api/notes', json={
            'title': 'a' * 101,
            'content': 'Valid content'
        }, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_note_content_validation(self):
        """Test content validation"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Content too long
        response = self.client.post('/api/notes', json={
            'title': 'Valid Title',
            'content': 'a' * 5001
        }, headers=headers)
        self.assertEqual(response.status_code, 400)

    # ======================== EDGE CASES ========================

    def test_authorization_header_missing(self):
        """Test request without Authorization header"""
        response = self.client.get('/api/notes')
        self.assertEqual(response.status_code, 401)

    def test_authorization_bearer_format_invalid(self):
        """Test invalid Bearer token format"""
        response = self.client.get('/api/notes',
            headers={'Authorization': 'InvalidFormat token'})
        self.assertEqual(response.status_code, 422)

    def test_pagination(self):
        """Test pagination in list notes"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create 5 notes
        for i in range(5):
            self.client.post('/api/notes', json={
                'title': f'Note {i}',
                'content': f'Content {i}'
            }, headers=headers)
        
        # Get first page with limit 2
        response = self.client.get('/api/notes?page=1&limit=2', headers=headers)
        payload = response.get_json()
        self.assertEqual(len(payload['data']), 2)
        self.assertEqual(payload['pagination']['total'], 5)
        self.assertEqual(payload['pagination']['page'], 1)

    def test_case_insensitive_duplicate_title(self):
        """Test that title duplicate check is case-insensitive"""
        # Register and get token
        reg_response = self.client.post('/api/auth/register', json={
            'email': self.user1_email,
            'password': self.user1_password
        })
        token = reg_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create note with title
        self.client.post('/api/notes', json={
            'title': 'Case Test Title',
            'content': 'Content'
        }, headers=headers)
        
        # Try to create with different case
        response = self.client.post('/api/notes', json={
            'title': 'case test title',
            'content': 'Different content'
        }, headers=headers)
        
        self.assertEqual(response.status_code, 409)


if __name__ == '__main__':
    unittest.main()

