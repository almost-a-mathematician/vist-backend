from django.db import models
from . managers import WishlistManager
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='images', blank=True, null=True)
    # password = models.CharField(blank=False)
    birth_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden_bd = models.BooleanField(default=False)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        blank=False
    )
    # username = models.CharField(max_length=20, blank=False)
    friends = models.ManyToManyField('User', through="UserFriend")

    def are_friends_with(self, find_friend_id):
        return UserFriend.objects.filter(
            models.Q(user__id=self.id, friend__id=find_friend_id)
            | models.Q(friend__id=self.id, user__id=find_friend_id)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.ForeignKey(User,related_name='friend', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} & {self.friend.username}'
    
    class Meta:
        verbose_name = 'Друзья'
        verbose_name_plural = 'Друг'

class Wishlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists') 
    name = models.CharField(max_length=50, blank=False)
    users = models.ManyToManyField(User, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    objects = WishlistManager()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Вишлист'
        verbose_name_plural = 'Вишлисты'

class Gift(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='gifts')
    name = models.CharField(max_length=50, blank=False)
    img = models.ImageField(upload_to='images', blank=False, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    link_url = models.URLField(max_length=200, blank=False)
    description = models.CharField(max_length=150, blank=True)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_priority = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Подарок'
        verbose_name_plural = 'Подарки'
    
class UserFriendRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='friend_request', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='sent'
    )
    rejected_by = models.ForeignKey(User, related_name='rejected_by', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.status
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'