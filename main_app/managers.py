from django.db import models
from django.db.models import Q


class WishlistManager(models.Manager):
    def get_visible_for(self, viewer_id):

        return self.filter(
                           Q(archived_at__isnull=True),
                            (Q(users__id=viewer_id) | Q(owner__id=viewer_id) | Q(users__isnull=True))).distinct() 
    
