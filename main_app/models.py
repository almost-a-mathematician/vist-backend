from django.db import models
from . managers import WishlistManager


class User(models.Model):
    profile_pic = models.ImageField(upload_to='images', blank=True, null=True)
    password = models.CharField(blank=False)
    birth_date = models.DateTimeField()
    created_at = models.DateTimeField()
    is_hidden_bd = models.BooleanField()
    username = models.CharField(max_length=20, blank=False)
    friends = models.ManyToManyField('User', through="UserFriend")

    def __str__(self):
        return self.username


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
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, blank=False)
    img = models.ImageField(upload_to='images', blank=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    link_url = models.URLField(max_length=200, blank=False)
    description = models.CharField(max_length=150, blank=False)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
