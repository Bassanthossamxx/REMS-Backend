from django.shortcuts import render
from rest_framework import generics
from .models import Owner
from .serializers import OwnerSerializer
from rest_framework.permissions import IsAdminUser

# Create your views here.

class OwnerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
