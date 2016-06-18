from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email), username=kwargs.get('username')
        )

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_admin = True
        account.save()

        return account


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)

    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)

    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.username

    def get_full_name(self):
        return ' '.join([self.username, self.email])

    def get_short_name(self):
        return self.first_name


class Quest(models.Model):
    name = models.CharField(max_length=40, unique=True)
    timelimit = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    photo = models.URLField(blank=True)

    # manager
    objects = models.Manager()

    # additional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = ['name']
    REQUIRED_FIELDS = ['timelimit']

    def __unicode__(self):
        return self.name


class Question(models.Model):
    photo = models.URLField()
    text = models.CharField(max_length=300)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    latitude = models.FloatField(_('Latitude'))
    longitude = models.FloatField(_('Longitude'))
    quest = models.ForeignKey(Quest, related_name='questions')

    # manager
    objects = models.Manager()

    # additional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

# Create your models here.
