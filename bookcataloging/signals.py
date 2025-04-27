from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(user_signed_up)
def add_user_to_patron_group(sender, request, user, **kwargs):
    patron_group, created = Group.objects.get_or_create(name='Patron')
    user.groups.add(patron_group)