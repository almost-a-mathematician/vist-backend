from rest_framework import serializers


from . models import User, Wishlist, Gift

class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('profile_pic', 'birth_date', 'created_at', 'is_hidden_bd', 'username')
   
class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True)

    class Meta:
        model = User
        fields = ('profile_pic', 'birth_date', 'created_at', 'is_hidden_bd', 'username', 'friends')
   

class WishlistSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    users = UserSerializer(many=True)

    class Meta:
        model = Wishlist
        fields = ('owner', 'name', 'users', 'archived_at')
    
class GiftSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer()
    booked_by = UserSerializer()
    
    class Meta:
        model = Gift
        fields = ('wishlist', 'name', 'img', 'price', 'link_url', 'description', 'booked_by')