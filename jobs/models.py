from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

# --------------------------
# Job Category
# --------------------------
class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --------------------------
# Job Tag
# --------------------------
class JobTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# --------------------------
# Company Profile
# --------------------------
class CompanyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_profile",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# --------------------------
# Job Model
# --------------------------
class Job(models.Model):
    EMPLOYMENT_TYPES = (
        ("full-time", "Full-time"),
        ("part-time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("temporary", "Temporary"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    )

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    requirements = models.TextField(help_text="List job requirements, skills, or qualifications")
    company_name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default="full-time")

    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default="USD")

    STATUS_CHOICES = (
        ("open", "Open"),
        ("closed", "Closed"),
        ("draft", "Draft"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
     # 🔹 New fields for filtering and relations
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    # 🔹 New fields for filtering
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    tags = models.ManyToManyField(JobTag, blank=True, related_name="jobs")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If a company profile is set but company_name is empty, sync the display name
        if getattr(self, "company", None) and not self.company_name:
            try:
                self.company_name = self.company.name
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["location"]),
        ]
