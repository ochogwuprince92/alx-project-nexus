from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from jobs.models import JobCategory, JobTag, CompanyProfile, Job
from rest_framework import status
User = get_user_model()

class JobModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.company = CompanyProfile.objects.create(user=self.user, name="Test Company")
        self.category = JobCategory.objects.create(name="Engineering")
        self.tag = JobTag.objects.create(name="Python")
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Develop APIs",
            requirements="Django, DRF",
            company_name="Test Company",
            posted_by=self.user,
            company=self.company,
            category=self.category
        )
        self.job.tags.add(self.tag)

    def test_job_str(self):
        self.assertEqual(str(self.job), "Backend Developer at Test Company")

    def test_category_slug_auto_created(self):
        self.assertEqual(self.category.slug, "engineering")

    def test_tag_slug_auto_created(self):
        self.assertEqual(self.tag.slug, "python")


class JobAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.category = JobCategory.objects.create(name="Engineering")
        self.job_data = {
            "title": "Backend Dev",
            "description": "Develop APIs",
            "requirements": "Django",
            "company_name": "Test Company",
            "posted_by": self.user.id,
            "category": self.category.id
        }

    def test_create_job(self):
        response = self.client.post("/api/jobs/", self.job_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Backend Dev")

    def test_list_jobs(self):
        Job.objects.create(title="Job1", description="desc", requirements="req", company_name="C1", posted_by=self.user)
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) >= 1)

class JobPaginationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.category = JobCategory.objects.create(name="Engineering")
        # Create multiple jobs to trigger pagination
        for i in range(15):
            Job.objects.create(
                title=f"Job {i}",
                description="desc",
                requirements="req",
                company_name="CompanyX",
                posted_by=self.user,
                category=self.category
            )

    def test_job_list_is_paginated(self):
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)   # standard DRF pagination format
        self.assertLessEqual(len(response.data["results"]), 10)  # page size