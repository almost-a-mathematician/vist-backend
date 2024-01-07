from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from . serializers import UserSerializer, WishlistSerializer, GiftSerializer, UserWithWishlistsSerializer, WishlistWithUsersSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from . models import User, Wishlist, Gift
from rest_framework.decorators import action
from django.db.models import Q
from django.db.models import prefetch_related_objects
from django.db.models import Prefetch
from . managers import WishlistManager

def index(request):

    return HttpResponse('Hello Vist!')

class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        viewer_id = request.headers["My-User-Id"]

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


class WishlistViewSet(viewsets.ViewSet):
    
    queryset = Wishlist.objects.all()
    
    def retrieve(self, request, pk):
        viewer_id = int(request.headers["My-User-Id"])

        filtered_queryset = Wishlist.objects.get_visible_for(viewer_id)

        wishlist = get_object_or_404(filtered_queryset, pk=pk)
        
        serializer_class = WishlistWithUsersSerializer if viewer_id == wishlist.owner.id else WishlistSerializer

        serializer = serializer_class(wishlist, context={'request': request})

        return Response(serializer.data)

    @action(detail=False, methods=['get'])

    def archived(self, request):
        viewer_id = request.headers['My-User-Id']

        queryset = Wishlist.objects.filter(owner__id=viewer_id, archived_at__isnull=False) # фолс значит информация в поле != null а = дата архивации 
        serializer = WishlistSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)


class GiftViewSet(viewsets.ViewSet):
    queryset = Gift.objects.all()

    def list(self, request):
        serializer = GiftSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        gift = get_object_or_404(self.queryset, pk=pk)
        serializer = GiftSerializer(gift, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def booked(self, request):
        viewer_id = request.headers['My-User-Id'] 

        queryset = Gift.objects.filter(booked_by__id=viewer_id)
        serializer = GiftSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)