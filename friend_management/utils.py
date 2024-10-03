from django.utils import timezone
from django.apps import apps
from django.db import models

from django.conf import settings

from friend_management.models import Friend, FriendRequest

from django.core.cache import cache

import pickle

from django.utils.crypto import get_random_string


class FriendshipManager:

    friends_cache_key = "friends_cache_{user_id}_{version}"
    friend_requests_cache_key = "friend_requests_cache_{user_id}_{sort}_{version}"
    friends_cache_timeout = 60 * 60 * 24
    friend_requests_cache_timeout = 60 * 60 * 24

    @classmethod
    def get_user_cache_version(cls, user_id, cache_type="friends"):
        """
        Retrieve or set a cache version (namespace) for the user. 
        This will help in grouping all cache keys for that user.
        """
        version_key = f"user_cache_version_{user_id}_{cache_type}"
        version = cache.get(version_key)
        if version is None:
            # If no version exists, generate a new one
            version = get_random_string(8)  # Can use a timestamp or random string
            cache.set(version_key, version, timeout=None)  # Version doesn't expire
        return version

    @classmethod
    def increment_user_cache_version(self, user_id, cache_type="friends"):
        """
        Invalidate all cached data for a user by changing their cache version.
        """
        version_key = f"user_cache_version_{user_id}_{cache_type}"
        new_version = get_random_string(8)
        cache.set(version_key, new_version, timeout=None)

    @classmethod
    def get_user_cache_version(cls, user_id, cache_type="friends"):
        """
        Retrieve or set a cache version (namespace) for the user. 
        This will help in grouping all cache keys for that user.
        """
        version_key = f"user_cache_version_{user_id}_{cache_type}"
        version = cache.get(version_key)
        if version is None:
            # If no version exists, generate a new one
            version = get_random_string(8)  # Can use a timestamp or random string
            cache.set(version_key, version, timeout=None)  # Version doesn't expire
        return version

    @classmethod
    def increment_user_cache_version(self, user_id, cache_type="friends"):
        """
        Invalidate all cached data for a user by changing their cache version.
        """
        version_key = f"user_cache_version_{user_id}_{cache_type}"
        new_version = get_random_string(8)
        cache.set(version_key, new_version, timeout=None)

    @classmethod
    def get_friends(cls, user):
        version = cls.get_user_cache_version(user.id, "friends")
        friends_cache_key = cls.friends_cache_key.format(user_id=user.id, version=version)
        friends = cache.get(friends_cache_key)
        if friends:
            return pickle.loads(friends)
        
        user_friends = Friend.objects.filter(user=user).values_list('friend', flat=True)
        user_friend_of = Friend.objects.filter(friend=user).values_list('user', flat=True)
        combined = list(user_friends) + list(user_friend_of)

        user_model = apps.get_model('accounts', 'CustomUser')
        friends = user_model.objects.filter(id__in=combined)

        cache.set(friends_cache_key, pickle.dumps(friends), cls.friends_cache_timeout)

        return friends
        
    @classmethod
    def are_friends(cls, user1, user2):
        user1_friends_cache_key = cls.friends_cache_key.format(user_id=user1.id, version=cls.get_user_cache_version(user1.id, "friends"))

        user1_friends = cache.get(user1_friends_cache_key)
        if user1_friends and user2.id in pickle.loads(user1_friends).values_list('id', flat=True):
            return True
        
        user2_friends_cache_key = cls.friends_cache_key.format(user_id=user2.id, version=cls.get_user_cache_version(user2.id, "friends"))
        
        user2_friends = cache.get(user2_friends_cache_key)
        if user2_friends and user1.id in pickle.loads(user2_friends).values_list('id', flat=True):
            return True
        
        return Friend.objects.filter(models.Q(user=user1, friend=user2) | models.Q(user=user2, friend=user1)).exists()
    
    @classmethod
    def add_friend(cls, from_user, to_user):
        if cls.are_friends(from_user, to_user):
            return False

        Friend.objects.create(user=from_user, friend=to_user)

        # invalidate cache
        cls.increment_user_cache_version(from_user.id, "friends")
        cls.increment_user_cache_version(to_user.id, "friends")

        return True

    @classmethod
    def remove_friend(cls, from_user, to_user):
        if not cls.are_friends(from_user, to_user):
            return False

        Friend.objects.filter(user=from_user, friend=to_user).delete()
        Friend.objects.filter(user=to_user, friend=from_user).delete()

        # invalidate cache
        cls.increment_user_cache_version(from_user.id, "friends")
        cls.increment_user_cache_version(to_user.id, "friends")

        return True
    
    @classmethod
    def get_friend_requests(cls, user, sort="created_at"):
        friend_requests_cache_key = cls.friend_requests_cache_key.format(user_id=user.id,
                                                                         sort=sort,
                                                                         version=cls.get_user_cache_version(user.id, "friend_requests")
                                                                        )
        friend_requests = cache.get(friend_requests_cache_key)
        if friend_requests:
            return pickle.loads(friend_requests)

        if sort.startswith("-"):
            sort_field = sort[1:]
        else:
            sort_field = sort

        if sort_field.startswith("from_user"):
            friend_requests = FriendRequest.objects.filter(to_user=user, status="pending").select_related('from_user').order_by(sort)
        else:
            friend_requests = FriendRequest.objects.filter(to_user=user, status="pending").select_related('to_user').order_by(sort)
        
        cache.set(friend_requests_cache_key, pickle.dumps(friend_requests), cls.friend_requests_cache_timeout)
        
        return friend_requests
    
    @classmethod
    def send_friend_request(cls, from_user, to_user):
        if from_user == to_user:
            return False
        
        if cls.are_friends(from_user, to_user):
            return False

        if FriendRequest.objects.filter(status="pending")\
            .filter(
                models.Q(from_user=from_user, to_user=to_user) |
                models.Q(from_user=to_user, to_user=from_user)
            ).exists():
            return False
        
        if FriendRequest.objects.filter(status="rejected")\
            .filter(from_user=from_user, to_user=to_user).filter(rejected_at__gte=timezone.now()
                                                                  - timezone.timedelta(hours=settings.FRIEND_REQUEST_TIMEOUT)).exists():
            return False

        FriendRequest.objects.create(from_user=from_user, to_user=to_user)

        # invalidate cache
        cls.increment_user_cache_version(to_user.id, "friend_requests")

        return True
    
    @classmethod
    def accept_friend_request(cls, friend_request):
        friend_request.status = "accepted"
        friend_request.save()

        cls.add_friend(friend_request.from_user, friend_request.to_user)

        # invalidate cache
        cls.increment_user_cache_version(friend_request.to_user.id, "friend_requests")
        cls.increment_user_cache_version(friend_request.from_user.id, "friends")
        cls.increment_user_cache_version(friend_request.to_user.id, "friends")

        return True
    
    @classmethod
    def reject_friend_request(cls, friend_request):
        friend_request.status = "rejected"
        friend_request.rejected_at = timezone.timezone.now()
        friend_request.save()

        # invalidate cache
        cls.increment_user_cache_version(friend_request.to_user.id, "friend_requests")

        return True