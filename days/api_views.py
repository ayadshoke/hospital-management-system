from rest_framework.response import Response
from rest_framework import status,filters
from .serializer import DaySerializer
from departs.models import Days
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

@api_view(['GET','POST'])
def al_days(request):
    if request.method == 'GET':
        all_days = Days.objects.filter(available=True).order_by('day')
        serializer = DaySerializer(all_days,many=True)

        data = {'عدد الايام ':all_days.count(),'الايام ':serializer.data}
        return Response(data,status=status.HTTP_200_OK)
    if request.method == 'POST': # دي لازم تبقي بالشكل ده
        serializer = DaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT','PATCH','DELETE'])
def al_days_id(request,id):
    if request.method == 'GET':  # دي لازم تبقي بالشكل ده
        item = Days.objects.get(pk=id)
        serializer =DaySerializer(instance=item)
        return Response(serializer.data,status=status.HTTP_200_OK)

    if request.method == 'PUT':  # دي لازم تبقي بالشكل ده
        item = Days.objects.get(pk=id)
        serializer =DaySerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

    if request.method == 'PATCH':  # دي لازم تبقي بالشكل ده
        item = Days.objects.get(pk=id)
        serializer =DaySerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

    if request.method == 'PUT':  # دي لازم تبقي بالشكل ده
        item = Days.objects.get(pk=id)
        item.delete()
        return Response({'message':'item deleted'})

"""النوع الثاني """
class Api_days(APIView):
    def get(self,request):
        all_days = Days.objects.filter(available=True).order_by('day')
        serializer = DaySerializer(all_days, many=True)

        data = {'عدد الايام ': all_days.count(), 'الايام ': serializer.data}
        return Response(data, status=status.HTTP_200_OK)
    def post(self,request):
        serializer = DaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class Api_days_id(APIView):
    def get(self,request,id):
        item = Days.objects.get(pk=id)
        serializer = DaySerializer(instance=item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request,id):
        item = Days.objects.get(pk=id)
        serializer = DaySerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    def patch(self,request,id):
        item = Days.objects.get(pk=id)
        serializer = DaySerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    def delete(self,request,id):
        item = Days.objects.get(pk=id)
        item.delete()
        return Response({'message': 'item deleted'})

"""النوع الثالث
generics"""
class Gen_days(ListCreateAPIView):
    queryset = Days.objects.filter(available=True).order_by('day')
    serializer_class = DaySerializer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    filterset_fields =['day']
    ordering_fields = ['pk','day']
    search_fields =['day','doctor']

class Gen_days_id(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = Days.objects.filter(available=True).order_by('day')
    serializer_class = DaySerializer

""" النوع الرابع
"""
class View_days(ModelViewSet):
    queryset = Days.objects.filter(available=True).order_by('day')
    serializer_class = DaySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['day']
    ordering_fields = ['pk', 'day']
    search_fields = ['day', 'doctor']









