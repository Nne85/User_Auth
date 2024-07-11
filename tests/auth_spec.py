import unittest
import json
import logging
from app import create_app, db
from flask_jwt_extended import decode_token
from datetime import datetime, timedelta
from models.user import User
from models.organisation import Organisation
from pytz import timezone as pytz_timezone

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Setup test database
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_success(self):
        """ Test successful user registration with default organisation. """
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
            })

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        user = User.query.filter_by(email=data['data']['user']['email']).first()

        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Registration successful')
        self.assertIn('accessToken', data['data'])
        self.assertEqual(data['data']['user']['firstName'], 'John')
        self.assertEqual(data['data']['user']['lastName'], 'Doe')
        self.assertEqual(data['data']['user']['email'], 'john.doe@example.com')

        # Check default organisation
        user = User.query.filter_by(email='john.doe@example.com').first()
        org = Organisation.query.filter_by(ownerId=user.userId).first()
        self.assertEqual(org.name, "John's Organisation")

    def test_login_success(self):
        """Test successful user login"""
        self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane@example.com',
            'password': 'password123',
            'phone': '0987654321'
        })
        response = self.client.post('/auth/login', json={
            'email': 'jane@example.com',
            'password': 'password123'
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('accessToken', data['data'])
        self.assertIn('user', data['data'])
        self.assertEqual(data['data']['user']['email'], 'jane@example.com')

    def test_login_failure(self):
        """Test login failure with incorrect credentials"""
        response = self.client.post('/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['status'], 'Bad request')
        self.assertEqual(data['message'], 'Authentication failed')

    def test_register_missing_fields(self):
        """Test registration failure when required fields are missing"""
        required_fields = ['firstName', 'lastName', 'email', 'password']

        for field in required_fields:
            data = {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john.doe@example.com',
                'password': 'password123'
            }
            data.pop(field)
            response = self.client.post('/auth/register', json=data)
            self.assertEqual(response.status_code, 422)
            error_data = json.loads(response.data)
            self.assertIn('errors', error_data)
            self.assertEqual(error_data['errors'][0]['field'], field)
            self.assertIn('required', error_data['errors'][0]['message'])

    def test_register_duplicate_email(self):
        """ Test registration failure with duplicate email. """
        self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })

        response = self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password456'
        })


        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'Bad request')
        self.assertEqual(data['message'], 'Registration unsuccessful')

    def test_token_expiration(self):
        """Test that the generated token expires at the correct time"""
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'

        })
        data = json.loads(response.data)
        token = data['data']['accessToken']
        decoded_token = decode_token(token)
        expiration_time = datetime.fromtimestamp(decoded_token['exp'], tz=pytz_timezone('UTC'))
        expected_expiration = datetime.now(pytz_timezone('UTC')) + timedelta(minutes=15)

        self.assertAlmostEqual(expiration_time, expected_expiration, delta=timedelta(seconds=5))


    def test_token_user_details(self):
        """Test that the correct user details are found in the token"""
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        data = json.loads(response.data)
        token = data['data']['accessToken']

        decoded_token = decode_token(token)
        self.assertEqual(decoded_token['sub'], data['data']['user']['userId'])


    def test_organisation_access(self):
        """Test that users can't see data from organisations they don't have access to"""
        # Register two users
        self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'

        })
        self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane@example.com',
            'password': 'password456'
        })

        # Login as John
        response = self.client.post('/auth/login', json={
            'email': 'john@example.com',
            'password': 'password123'
        })

        john_token = json.loads(response.data)['data']['accessToken']
        # Get John's organisations
        response = self.client.get('/api/organisations', headers={'Authorization': f'Bearer {john_token}'})
        john_orgs = json.loads(response.data)['data']['organisations']
        print(f"John's organisations: {john_orgs}")

        # Login as Jane
        response = self.client.post('/auth/login', json={
            'email': 'jane@example.com',
            'password': 'password456'
        })
        jane_token = json.loads(response.data)['data']['accessToken']

        # Try to access John's organisation as Jane
        response = self.client.get(f'/api/organisations/{john_orgs[0]["orgId"]}', headers={'Authorization': f'Bearer {jane_token}'})
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'Bad request')
        self.assertEqual(data['message'], 'Organisation not found or access denied')

        response = self.client.get(f'/api/organisations/{john_orgs[0]["orgId"]}', headers={'Authorization': f'Bearer {john_token}'})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
