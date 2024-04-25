from . views import UserViewSet, WishlistViewSet, GiftViewSet, UserAndWishlistSearchViewSet, FriendRequestViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'gifts', GiftViewSet, basename='gift')
router.register(r'search', UserAndWishlistSearchViewSet, basename='search')
router.register(r'friend_requests', FriendRequestViewSet, basename='friend_requests')


