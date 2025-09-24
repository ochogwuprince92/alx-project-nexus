from django.test import TestCase, Client


class SchemaSmokeTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_openapi_json_available(self):
        response = self.client.get("/openapi/")
        self.assertEqual(response.status_code, 200)
        # content may be OpenAPI v3 (contains 'openapi') or drf-yasg may return swagger: '2.0' YAML
        body = response.content.lower()
        self.assertTrue(b"openapi" in body or b"swagger" in body)

    def test_swagger_ui_available(self):
        response = self.client.get("/swagger/")
        self.assertEqual(response.status_code, 200)
        # ensure the swagger UI script shows up
        self.assertIn(b"swagger-ui", response.content.lower())
