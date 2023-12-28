from . views import UserViewSet, WishlistViewSet, GiftViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'gifts', GiftViewSet, basename='gift')



