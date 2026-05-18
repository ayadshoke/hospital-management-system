from django.db.models import Sum
from rest_framework import status,filters
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from departs.models import Doctors,Payment
from .serializer import DocSerializer,DocNameSerializer


@api_view(['GET', 'POST'])
def api_doc(request):
    if request.method == 'GET':
        total_amount = Payment.objects.aggregate(total=Sum('amount'))
        all_doc = Doctors.objects.all().count()
        doctors = Doctors.objects.filter(appointments__isnull=True)
        docs = Doctors.objects.filter(appointments__isnull=False).distinct().order_by('pk')
        serializer1 = DocSerializer(docs, many=True)
        serializer2 = DocNameSerializer(doctors, many=True)

        context ={'اجمالي عدد الدكاتره':all_doc,'عدد دكاترة بدون حجز':doctors.count()
            ,'دكاتر بدون حجز':serializer2.data,
                ' عدد دكاتره تعمل':docs.count(),'total_amount':total_amount,
                  'دكاترة تعمل':serializer1.data}



        return Response(context, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = DocSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'item added successfully','data':serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET','PUT','PATCH','DELETE'])
def api_doc_pk(request,id):
    item = Doctors.objects.get(pk=id)
    if request.method == 'GET':
        serializer = DocSerializer(instance=item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        serializer = DocSerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'item edited','data':serializer.data},status=status.HTTP_202_ACCEPTED)

    if request.method == 'PATCH':
        serializer = DocSerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'item edited','data':serializer.data},status=status.HTTP_202_ACCEPTED)

    if request.method == 'DELETE':
        item.delete()
        return Response({'message': 'deleted'})

"""النوع الثاني
class based view APIview
"""
class Doc_list(APIView):
    def get(self,request):
        docs = Doctors.objects.filter(appointments__isnull=False).distinct().order_by('pk')
        serializer = DocSerializer(docs,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request):
        serializer = DocSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'item added successfully', 'data': serializer.data},status=status.HTTP_201_CREATED)

class Doc_list_pk(APIView):
    def get(self,request,id):
        item = Doctors.objects.get(pk=id)
        serializer = DocSerializer(instance=item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request,id):
        item = Doctors.objects.get(pk=id)
        serializer = DocSerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'item edit successfully', 'data': serializer.data},status=status.HTTP_201_CREATED)
    def patch(self,request,id):
        item = Doctors.objects.get(pk=id)
        serializer = DocSerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'item edit successfully', 'data': serializer.data},status=status.HTTP_201_CREATED)
    def delete(self,request,id):
        item = Doctors.objects.get(pk=id)
        item.delete()
        return Response({'message': 'deleted'})

"""
النوع الثالث generic views 
"""
class Gen_doc(ListCreateAPIView):
    queryset = Doctors.objects.filter(appointments__isnull=False).distinct().order_by('pk')
    serializer_class = DocSerializer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    filterset_fields = ['id','name','part']# هنا لازم نكتب id وليس pk مهم
    ordering_fields = ['pk','name','part']
    search_fields = ['name','part','email']

class Gen_doc_pk(RetrieveUpdateDestroyAPIView):
    # lookup_field = 'id' # الكود ده علشان لو عايز تستخدم id بدلا من pk اللي الاساسي
    queryset = Doctors.objects.all()
    serializer_class = DocSerializer

class ViewSet_doc(ModelViewSet):
    queryset = Doctors.objects.filter(appointments__isnull=False).distinct().order_by('pk')
    serializer_class = DocSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['id', 'name', 'part']  # هنا لازم نكتب id وليس pk مهم
    ordering_fields = ['pk', 'name', 'part']
    search_fields = ['name', 'part', 'email']










