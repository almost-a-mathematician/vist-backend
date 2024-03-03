from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from . serializers import UserSerializer, WishlistSerializer, GiftSerializer, UserWithWishlistsSerializer, WishlistWithUsersSerializer, RegisterSerializer,LoginSerializer,LogoutSerializer
from rest_framework import viewsets, generics, status, views, permissions
from rest_framework.response import Response
from . models import User, Wishlist, Gift
from rest_framework.decorators import action, api_view, parser_classes
from django.db.models import Q
from django.db.models import prefetch_related_objects
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        viewer_id = request.user.id

        user = get_object_or_404(self.queryset, pk=pk)
        
        wishlists = Wishlist.objects.get_visible_for(viewer_id)
                                          
        prefetch_related_objects([user], Prefetch('wishlists', wishlists))

        serializer = UserWithWishlistsSerializer(user, context={'request': request})

        return Response(serializer.data)
    
        '''
        ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ 

        * попробовать определить переменную wishlists через user.wishlists
        * попробовать обойтись без функции prefetch_related_objects() в пользу user.wishlists = user.wishlists.filter(...),
        либо просто через user.wishlists.filter(...)
        '''
        
    def partial_update(self, request, pk):
        viewer_id = request.user.id

        if viewer_id != int(pk):
            raise PermissionDenied()
 
        # находим пользователя по pk
        user = get_object_or_404(self.queryset, pk=pk) 

        serializer = UserWithWishlistsSerializer( 
            user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        serializer.save()
        
        return Response(serializer.data)
    
class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Wishlist.objects.all()
    
    def retrieve(self, request, pk):
        viewer_id = request.user.id

        filtered_queryset = Wishlist.objects.get_visible_for(viewer_id)

        wishlist = get_object_or_404(filtered_queryset, pk=pk)
            
        # sezrializer_class = WishlistWithUsersSerializer if viewer_id == wishlist.owner.id else WishlistSerializer

        serializer_class = self.choose_wishlist_serializer(viewer_id, wishlist)

        serializer = serializer_class(wishlist, context={'request': request})

        return Response(serializer.data)
    
    def choose_wishlist_serializer(self, viewer_id, wishlist):
           if viewer_id == wishlist.owner.id:
               return WishlistWithUsersSerializer
           else:
               return WishlistSerializer


    @action(detail=False, methods=['get'])

    def archived(self, request):
        viewer_id = request.user.id

        queryset = Wishlist.objects.filter(owner__id=viewer_id, archived_at__isnull=False) # фолс значит информация в поле != null а = дата архивации 
        serializer = WishlistSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)
    
    def partial_update(self, request, pk):
        viewer_id = request.user.id

        wishlist = get_object_or_404(self.queryset, pk=pk)

        if viewer_id != wishlist.owner.id:
            raise PermissionDenied()

        serializer = WishlistWithUsersSerializer(
            wishlist,
            data=request.data, 
            partial=True, 
            context={'request': request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        serializer.save()

        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], url_path='users')

    def update_wishlist_users(self, request, pk):
        viewer_id = request.user.id

        filtered_queryset = Wishlist.objects.get_visible_for(viewer_id)
   
        wishlist = get_object_or_404(filtered_queryset, pk=pk)

        if viewer_id != wishlist.owner.id:
            raise PermissionDenied()

        request_users = request.data
        

        if wishlist.owner.id in request_users and len(request_users) > 1:
            request_users.remove(wishlist.owner.id)

        new_users_list = User.objects.filter(id__in=request_users)

        wishlist.users.set(new_users_list)

        wishlist.save()

        serializer = WishlistWithUsersSerializer(
            wishlist,
            context={'request': request}
        )

        return Response(serializer.data)

    def create(self, request):
        viewer_id = request.user.id
        viewer = User.objects.get(id=viewer_id)

        wishlist = Wishlist.objects.create(
            owner=viewer
        )

        serializer = WishlistWithUsersSerializer(
            wishlist,
            data=request.data, 
            partial=True, 
            context={'request': request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        serializer.save()

        return Response(serializer.data)

class GiftViewSet(viewsets.ViewSet):
    queryset = Gift.objects.all()
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='booked')

    def booked(self, request):
        viewer_id = request.user.id 

        queryset = Gift.objects.filter(booked_by__id=viewer_id)

        serializer = GiftSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)
    
    def partial_update(self, request, pk):
        viewer_id = request.user.id

        gift = get_object_or_404(self.queryset, pk=pk)

        if viewer_id != gift.wishlist.owner.id:
            raise PermissionDenied()
        
        serializer = GiftSerializer(
            gift, 
            data = request.data, 
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.error)
        
        serializer.save()

        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='booked_by')

    def gift_was_booked_by(self, request, pk):
        viewer_id = request.user.id

        visible_wishlist = Wishlist.objects.get_visible_for(viewer_id)

        gift = get_object_or_404(self.queryset, pk=pk)

        gift_owner = gift.wishlist.owner

        if not visible_wishlist.filter(gifts__id=pk).exists():
            raise PermissionDenied
        
        if viewer_id != gift_owner.id and gift_owner.are_friends_with(viewer_id) == False:
            raise PermissionDenied

        if viewer_id != gift_owner.id and gift.booked_by != None and gift.booked_by.id != viewer_id:
            raise PermissionDenied
        
        if request.data == None:
            gift.booked_by = None
        else:
            gift.booked_by = User.objects.get(id=viewer_id)

        gift.save()
        
        serializer = GiftSerializer(gift, context={'request': request})

        return Response(serializer.data)

    def create(self, request):
        viewer_id = request.user.id

        queryset = Wishlist.objects.all()

        wishlist = get_object_or_404(queryset, pk=request.data['wishlist'])

        if wishlist.owner.id != viewer_id:
            raise PermissionDenied
            
        serializer = GiftSerializer(
            data=request.data,  
            context={'request': request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        viewer_id = request.user.id

        gift = get_object_or_404(self.queryset, pk=pk)
        
        if viewer_id == gift.wishlist.owner.id:
            gift.delete()
        else:
            raise PermissionDenied
        
        return Response()
    
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    
    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated, )
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)