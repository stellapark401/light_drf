from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class Hello(APIView):

    def get(self, request):
        return Response({'message': 'Hello World'})


class Home(APIView):

    @staticmethod
    def get(request):
        return Response({'greeting': 'Welcome to Stepia :)'})

class Connection(APIView):

    @staticmethod
    def get(request):
        return Response({'connection': 'successful'})
