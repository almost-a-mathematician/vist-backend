from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from . serializers import UserSerializer, WishlistSerializer, GiftSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from . models import User, Wishlist, Gift
from rest_framework.decorators import action


def index(request):

    return HttpResponse('Hello Vist!')

class UserViewSet(viewsets.ModelViewSet):
    
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)



class WishlistViewSet(viewsets.ModelViewSet):

    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()

    def list(self, request):
        serializer = WishlistSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        wishlist = get_object_or_404(self.queryset, pk)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])

    def archived(self, request):
        viewer_id = request.headers['My-User-Id']

        queryset = Wishlist.objects.filter(archived_at__id=viewer_id)
        serializer =WishlistSerializer(queryset, many=True)

        return Response(serializer.data)


class GiftViewSet(viewsets.ModelViewSet):

    serializer_class = GiftSerializer
    queryset = Gift.objects.all()

    def list(self, request):
        serializer = GiftSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        gift = get_object_or_404(self.queryset, pk)
        serializer = GiftSerializer(gift)
        return Response(serializer.data)

    @action(detail=False, methods=['get']) # это декоратор. detail=False значит, что действие происходит над списком, т.е не /gifts/{id}/booked а /gifts/booked и methods=["get"] это массив допустимых методов, в нашем случае мы только ожидаем GET

    def booked(self, request):
        viewer_id = request.headers['My-User-Id'] # получаем id юзера на который претендует отправляющий запрос, чтобы вообразить что это на самом деле он

        queryset = Gift.objects.filter(booked_by__id=viewer_id) # получаем все подарки, у которых booked_by есть и его id равен viewer_id, т.е фактически подарок, айдишник забронированного который наш
        serializer = GiftSerializer(queryset, many=True)

        return Response(serializer.data)