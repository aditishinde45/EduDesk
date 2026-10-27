import unittest
import os
import datetime
from app import create_app
from extensions import db
from models import User, Student, Certificate

class EduDeskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF in tests for clean POSTs
        self.client = self.app.test_client()

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # -------------------------------------------------------------------------
    # 1. Public Verification Tests (No Login Required)
    # -------------------------------------------------------------------------
    def test_public_verify_page(self):
        response = self.client.get('/verify')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Certificate Verification Portal', response.data)

    def test_public_verify_active_certificate(self):
        response = self.client.get('/verify/KKW-2024-00001')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'VALID & GENUINE CERTIFICATE', response.data)
        self.assertIn(b'Aditi Shinde', response.data)
        self.assertIn(b'2200490001', response.data)

    def test_public_verify_expired_certificate(self):
        response = self.client.get('/verify/KKW-2023-00012')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EXPIRED CERTIFICATE', response.data)

    def test_public_verify_revoked_certificate(self):
        response = self.client.get('/verify/KKW-2024-00008')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'REVOKED / INVALID CERTIFICATE', response.data)
        self.assertIn(b'Falsified attendance', response.data)

    def test_public_verify_nonexistent(self):
        response = self.client.get('/verify/INVALID-99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'NO RECORD FOUND', response.data)

    def test_unauthenticated_protected_route_redirects(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    # -------------------------------------------------------------------------
    # 2. Admin Role Permissions
    # -------------------------------------------------------------------------
    def test_admin_permissions(self):
        login_res = self.login('admin', 'admin123')
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Institution Overview', login_res.data)

        # Admin can access all modules
        self.assertEqual(self.client.get('/departments/').status_code, 200)
        self.assertEqual(self.client.get('/departments/add').status_code, 200)
        self.assertEqual(self.client.get('/courses/').status_code, 200)
        self.assertEqual(self.client.get('/courses/add').status_code, 200)
        self.assertEqual(self.client.get('/certificate-types/').status_code, 200)
        self.assertEqual(self.client.get('/authorities/').status_code, 200)
        self.assertEqual(self.client.get('/students/').status_code, 200)
        self.assertEqual(self.client.get('/students/add').status_code, 200)
        self.assertEqual(self.client.get('/certificates/').status_code, 200)
        self.assertEqual(self.client.get('/certificates/add').status_code, 200)
        self.assertEqual(self.client.get('/users/').status_code, 200)
        self.assertEqual(self.client.get('/audit-logs/').status_code, 200)
        self.assertEqual(self.client.get('/reports/issued').status_code, 200)
        self.assertEqual(self.client.get('/reports/expired').status_code, 200)
        self.assertEqual(self.client.get('/reports/summary').status_code, 200)

        self.logout()

    # -------------------------------------------------------------------------
    # 3. Staff Role Permissions & Enforcements
    # -------------------------------------------------------------------------
    def test_staff_permissions(self):
        self.login('staff', 'staff123')

        # Staff can read departments and courses
        self.assertEqual(self.client.get('/departments/').status_code, 200)
        self.assertEqual(self.client.get('/courses/').status_code, 200)

        # Staff CANNOT add departments or courses (Admin only -> 403)
        self.assertEqual(self.client.get('/departments/add').status_code, 403)
        self.assertEqual(self.client.get('/courses/add').status_code, 403)

        # Staff can manage certificate types and authorities
        self.assertEqual(self.client.get('/certificate-types/').status_code, 200)
        self.assertEqual(self.client.get('/authorities/').status_code, 200)

        # Staff can read and create students & certificates
        self.assertEqual(self.client.get('/students/').status_code, 200)
        self.assertEqual(self.client.get('/students/add').status_code, 200)
        self.assertEqual(self.client.get('/certificates/').status_code, 200)
        self.assertEqual(self.client.get('/certificates/add').status_code, 200)

        # Staff CANNOT delete students or certificates (Admin only -> 403)
        self.assertEqual(self.client.post('/students/1/delete').status_code, 403)
        self.assertEqual(self.client.post('/certificates/1/delete').status_code, 403)

        # Staff CANNOT access Users or Audit logs (Admin only -> 403)
        self.assertEqual(self.client.get('/users/').status_code, 403)
        self.assertEqual(self.client.get('/audit-logs/').status_code, 403)

        # Staff CAN access reports
        self.assertEqual(self.client.get('/reports/issued').status_code, 200)
        self.assertEqual(self.client.get('/reports/summary').status_code, 200)

        self.logout()

    # -------------------------------------------------------------------------
    # 4. Student Role Permissions & Strict Isolation
    # -------------------------------------------------------------------------
    def test_student_permissions_and_isolation(self):
        login_res = self.login('student', 'student123')
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Student Portal', login_res.data)

        # Student CAN view their own profile and certificates
        self.assertEqual(self.client.get('/students/profile').status_code, 200)
        self.assertEqual(self.client.get('/certificates/').status_code, 200)

        # Student CANNOT access administrative / staff modules (all 403)
        self.assertEqual(self.client.get('/departments/').status_code, 403)
        self.assertEqual(self.client.get('/courses/').status_code, 403)
        self.assertEqual(self.client.get('/certificate-types/').status_code, 403)
        self.assertEqual(self.client.get('/authorities/').status_code, 403)
        self.assertEqual(self.client.get('/students/').status_code, 403)
        self.assertEqual(self.client.get('/users/').status_code, 403)
        self.assertEqual(self.client.get('/audit-logs/').status_code, 403)
        self.assertEqual(self.client.get('/reports/issued').status_code, 403)

        # Student can view their OWN certificate detail
        # Cert 1 belongs to student 1 (Aditi Shinde)
        self.assertEqual(self.client.get('/certificates/1').status_code, 200)

        # Student CANNOT view another student's certificate detail (Cert 3 belongs to student 2 -> 403 Forbidden)
        self.assertEqual(self.client.get('/certificates/3').status_code, 403)

        self.logout()

    # -------------------------------------------------------------------------
    # 5. Dynamic Course by Department Endpoint
    # -------------------------------------------------------------------------
    def test_courses_by_department_api(self):
        self.login('admin', 'admin123')
        with self.app.app_context():
            from models import Department
            dept = Department.query.first()
            dept_id = dept.Department_ID if dept else 1

        response = self.client.get(f'/courses/by-department/{dept_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertIn('name', data[0])
        self.logout()

if __name__ == '__main__':
    unittest.main()
