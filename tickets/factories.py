from datetime import tzinfo
from random import choices
import random
import factory
from django.contrib.auth.models import User
from django.template.defaultfilters import length
from django.utils import timezone
from factory.django import DjangoModelFactory
from .models import *
from .choices import PRIORITY_CHOICES


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    # username = factory.Sequence(lambda n: f"user{n}")
    username = factory.faker.Faker("user_name")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_active = factory.Faker("boolean")
    last_login = factory.Faker("date_time_this_decade", tzinfo=timezone.get_current_timezone())


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('name')
    is_active = factory.Faker('boolean')
    #created_at = factory.Faker('date_time_between', start_date='-2y', end_date='now')
    #updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')



class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker('word', locale='fa')


class TicketFactory(DjangoModelFactory):
    class Meta:
        model = Ticket

    category = factory.SubFactory(CategoryFactory)
    created_by = factory.SubFactory(UserFactory)
    priority = factory.Iterator([choices[0] for choices in PRIORITY_CHOICES])
    subject = factory.Faker("sentence", nb_words=12)
    description = factory.Faker("paragraph")
    max_reply_date = factory.Faker("future_datetime", tzinfo=timezone.get_current_timezone())


class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assignment

    assigned_ticket = factory.Iterator(Ticket.objects.all())
    assignee = factory.Iterator(User.objects.all())
    seen_at = factory.Faker("future_datetime", tzinfo=timezone.get_current_timezone())
    status = factory.Iterator([choices[0] for choices in STATUS_CHOICES])
    description = factory.Faker("sentence")