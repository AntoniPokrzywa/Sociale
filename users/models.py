from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        is_active=False,
        is_verified=False,
        first_name=None,
        last_name=None,
    ):
        """Creates and returns user"""
        if not email:
            raise ValueError("The Email field is required")
        if not password:
            raise ValueError("The Password field is required")

        user = self.model(
            email=self.normalize_email(email.lower()),
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_verified=is_verified,
        )

        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and returns superuser"""
        user = self.create_user(
            email=email, password=password, is_active=True, is_verified=True
        )

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)

    joined_at = models.DateTimeField(verbose_name="date joined", default=timezone.now)
    verified_at = models.DateTimeField(
        verbose_name="date verified", null=True, blank=True
    )
    last_active_at = models.DateTimeField(
        verbose_name="last active", default=timezone.now
    )

    is_active = models.BooleanField(verbose_name="active user", default=False)
    is_verified = models.BooleanField(verbose_name="verified email", default=False)
    is_staff = models.BooleanField(verbose_name="admin", default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def deactivate(self):
        self.is_active = False
        self.full_clean()
        self.save(update_fields=["is_active"])

    def verify(self):
        self.verified_at = timezone.now()
        self.is_verified = True
        self.full_clean()
        self.save(update_fields=["verified_at", "is_verified"])

    def activate(self):
        self.is_active = True
        self.full_clean()
        self.save(update_fields=["is_active"])

    @property
    def is_eligible(self):
        return self.is_active and self.is_verified
