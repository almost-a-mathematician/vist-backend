from rest_framework import serializers
from . models import User, Wishlist, Gift
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_pic', 'birth_date')

class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_pic', 'birth_date', 'friends', 'is_hidden_bd')

    # переопределеяем метод to_representation сериализатора
    def to_representation(self, instance):
        # вызываем метод to_representation наследуемого класса
        # это нужно для того чтобы так раз таки выполнить
        # дефолтный механизм приведения модели instance в
        # сериализируемый тип данных data
       
        data = super().to_representation(instance)
        
        request = self.context['request']
        viewer_id = request.user.id

        if viewer_id != instance.id and instance.is_hidden_bd==True:
            data.pop('birth_date')
        

        # на этом моменте мы имеем data, которая сама по себе
        # является OrderedDict, т.е упорядоченным dict (сейчас не
        # важно что он упорядоченный, в целом это обычный dict с
        # упорядочиванием ключей в нем)
        # Задача: удалить поле birth_date из data, если у модели
        # пользователя (instance) отключено отображение даты рождения

        return data
class GiftSerializer(serializers.ModelSerializer):
    booked_by = UserSerializer(required=False)
    owner = serializers.    SerializerMethodField() 
    class Meta:
        model = Gift
        fields = ('id', 'name', 'wishlist', 'img', 'price', 'link_url', 'description', 'booked_by', 'owner')

    def get_owner(self, obj):
        owner = obj.wishlist.owner
        serializer = UserSerializer(owner, context=self.context)
        return serializer.data

class WishlistSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    gifts = GiftSerializer(many=True)
    class Meta:
        model = Wishlist
        fields = ('id', 'name', 'owner', 'gifts', 'archived_at')

class UserWithWishlistsSerializer(UserSerializer):
    wishlists = WishlistSerializer(many=True) 

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('wishlists', )
        
class WishlistWithUsersSerializer(WishlistSerializer):
    users = UserSerializer(many=True)

    class Meta(WishlistSerializer.Meta):
        fields = WishlistSerializer.Meta.fields + ('users', )

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=4, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'birth_date', 'profile_pic']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=4,write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()
    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return user.tokens()
    class Meta:
        model = User
        fields = ['password','username','tokens']
    def validate(self, attrs):
        username = attrs.get('username','')
        password = attrs.get('password','')
        user = auth.authenticate(username=username,password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
