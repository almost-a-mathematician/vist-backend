from django.db import models
from . managers import WishlistManager
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='images', blank=True, null=True)
    # password = models.CharField(blank=False)
    birth_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden_bd = models.BooleanField(default=False)
    # username = models.CharField(max_length=20, blank=False)
    friends = models.ManyToManyField('User', through="UserFriend")

    def are_friends_with(self, find_friend_id):
        return UserFriend.objects.filter(
            models.Q(user__id=self.id, friend__id=find_friend_id)
            | models.Q(friend__id=self.id, user__id=find_friend_id),
            status='accepted'
        ).exists()
    
    def __str__(self):
        return self.username
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }
 
class UserFriend(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.ForeignKey(User,related_name='friend', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='sent'
    )

    def __str__(self):
        return self.status

class Wishlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists') 
    name = models.CharField(max_length=20, blank=False)
    users = models.ManyToManyField(User)
    archived_at = models.DateTimeField(null=True, blank=True)

    objects = WishlistManager()

    def __str__(self):
        return self.name

class Gift(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='gifts')
    name = models.CharField(max_length=20, blank=False)
    img = models.ImageField(upload_to='images', blank=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    link_url = models.URLField(max_length=200, blank=False)
    description = models.CharField(max_length=150, blank=True)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
    
