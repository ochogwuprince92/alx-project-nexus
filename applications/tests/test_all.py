from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.test import APIClient
from jobs.models import Job, JobCategory
from applications.models import JobApplication, Notification
from applications.serializers import JobApplicationSerializer
from rest_framework import status

User = get_user_model()


class JobApplicationModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass1234"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="pass1234"
        )
        self.category = JobCategory.objects.create(name="Engineering")
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Develop APIs",
            requirements="Django",
            company_name="Test Co",
            posted_by=self.user,
            category=self.category,
        )

    def test_unique_application(self):
        JobApplication.objects.create(user=self.user2, job=self.job)
        with self.assertRaises(Exception):
            JobApplication.objects.create(user=self.user2, job=self.job)


class JobApplicationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="pass1234"
        )
        self.client.force_authenticate(user=self.user)
        self.category = JobCategory.objects.create(name="Engineering")
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Develop APIs",
            requirements="Django",
            company_name="Test Co",
            posted_by=self.user,
            category=self.category,
        )

    @patch("applications.views.send_application_email_task.delay")
    def test_create_job_application(self, mock_send_email):
        data = {"job": self.job.id, "cover_letter": "I am interested"}
        response = self.client.post("/api/applications/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            JobApplication.objects.filter(user=self.user, job=self.job).exists()
        )
        # Celery task called
        mock_send_email.assert_called_once()

    def test_notifications_created(self):
        self.client.post(
            "/api/applications/",
            {"job": self.job.id, "cover_letter": "I am interested"},
        )
        self.assertEqual(
            Notification.objects.filter(recipient=self.job.posted_by).count(), 1
        )


class JobApplicationStatusUpdateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        self.user = User.objects.create_user(
            email="user@example.com", password="pass1234"
        )
        self.category = JobCategory.objects.create(name="Design")
        self.job = Job.objects.create(
            title="UI/UX Designer",
            description="Design cool UIs",
            requirements="Figma",
            company_name="Design Co",
            posted_by=self.admin,
            category=self.category,
        )
        self.application = JobApplication.objects.create(user=self.user, job=self.job)

    def test_admin_can_update_status(self):
        self.client.force_authenticate(user=self.admin)
        url = f"/api/applications/applications/{self.application.id}/status/"
        response = self.client.patch(url, {"status": "accepted"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "accepted")

    def test_non_admin_cannot_update_status(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/applications/applications/{self.application.id}/status/"
        response = self.client.patch(url, {"status": "accepted"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
