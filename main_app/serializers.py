from rest_framework import serializers


from . models import User, Wishlist, Gift

class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'profile_pic', 'birth_date')

class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_pic', 'birth_date', 'friends')

    # переопределеяем метод to_representation сериализатора
    def to_representation(self, instance):
        # вызываем метод to_representation наследуемого класса
        # это нужно для того чтобы так раз таки выполнить
        # дефолтный механизм приведения модели instance в
        # сериализируемый тип данных data
        print('lksfhkla', instance)
        data = super().to_representation(instance)
        print('ljfl;efjl;ewj;', data)

        request = self.context['request']

        print('GGGGGGGGG', request)

        viewer_id = int(request.headers['My-User-Id'])

        if viewer_id != instance.id and instance.is_hidden_bd==True:
            data.pop('birth_date')
        

        # на этом моменте мы имеем data, которая сама по себе
        # является OrderedDict, т.е упорядоченным dict (сейчас не
        # важно что он упорядоченный, в целом это обычный dict с
        # упорядочиванием ключей в нем)
        # Задача: удалить поле birth_date из data, если у модели
        # пользователя (instance) отключено отображение даты рождения

        return data
   
class WishlistSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Wishlist
        fields = ('id', 'name', 'owner', 'archived_at')
    
class GiftSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer()
    booked_by = UserSerializer()
    
    class Meta:
        model = Gift
        fields = ('id', 'name', 'wishlist', 'img', 'price', 'link_url', 'description', 'booked_by')

class UserWithWishlistsSerializer(UserSerializer):
    wishlists = WishlistSerializer(many=True) 

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('wishlists', )
        
class WishlistWithUsersSerializer(WishlistSerializer):
    users = UserSerializer(many=True)

    class Meta(WishlistSerializer.Meta):
        fields = WishlistSerializer.Meta.fields + ('users', )
