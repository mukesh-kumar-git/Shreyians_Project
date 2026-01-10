from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.utils.text import slugify


# -------------------- CUSTOM USER --------------------
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


User = settings.AUTH_USER_MODEL


# -------------------- COURSE --------------------
class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price_original = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_discounted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default="₹")
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=100, blank=True)
    schedule = models.CharField(max_length=255, blank=True)
    course_validity = models.CharField(max_length=255, blank=True)
    is_live = models.BooleanField(default=False)
    image = models.ImageField(upload_to="course_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField("CourseTag", blank=True, related_name="courses")

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# -------------------- COURSE TAG --------------------
class CourseTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# -------------------- CART --------------------
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"


# -------------------- CART ITEM --------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "course")

    def __str__(self):
        return self.course.title
