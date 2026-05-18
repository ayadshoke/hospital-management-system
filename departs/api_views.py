from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from .models import Departments
from .serializer import DepSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, generics


"""اول نوع
Functions Based Views FBV
"""
@api_view(['GET','POST'])
def show_departs(request):
    if request.method == 'GET':
        parts = Departments.objects.all().order_by('pk')
        serializer = DepSerializer(parts,many=True)# (data=parts,many=True)دي كده غلط ممنوع نستخدم كلمة data هنا
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = DepSerializer(data=request.data,status=status.HTTP_200_OK)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE','PATCH'])
def show_depart_pk(request,pk):
    item = Departments.objects.get(pk=pk)
    if request.method == 'GET':
        serializer = DepSerializer(instance=item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    # if request.method == 'PUT':
    #     serializer = DepSerializer(item,data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

    if request.method == 'PATCH':
        serializer = DepSerializer(instance=item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    if request.method == 'DELETE':
        item.delete()
        return Response({'message': 'deleted'})

"""النوع الثاني
CLASS BASED VIEW :APiv
"""
class View_parts(APIView):
    def get(self,request):
        parts = Departments.objects.all().order_by('pk')
        serializer = DepSerializer(parts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request):
        serializer = DepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

class View_parts_pk(APIView):
    def get(self,request,id):
        item = Departments.objects.get(pk=id)
        serializer = DepSerializer(instance=item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def patch(self,request,id):
        item = Departments.objects.get(pk=id)
        serializer = DepSerializer(instance=item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    def delete(self,request,id):
        item = Departments.objects.get(pk=id)
        item.delete()
        return Response({'message':'deleted'})

"""النوع الثالث 
GENERIC VIEWS
"""
class api_depart(generics.ListCreateAPIView):
    serializer_class = DepSerializer
    # queryset = Departments.objects.all()
    # queryset = Departments.objects.prefetch_related('doctors_set__part').annotate(doc_count=Count('pk')).filter(doc_count__gt=0)
    queryset = Departments.objects.prefetch_related('doctors_set').exclude(doctors__isnull=True).distinct()
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['name','floor']
    ordering_fields = ['pk']
    search_fields = ['name','floor']
    def get_queryset(self):
        queryset = super().get_queryset()
        look_for = self.request.GET.get('floor')
        dep = self.request.GET.get('dep')
        if look_for:
            queryset = queryset.filter(floor=look_for)
        if dep:
            queryset = queryset.filter(name__icontains=dep)
        # serializer = serializer_class(queryset, many=True)
        return queryset

class api_dep_update(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepSerializer
    queryset = Departments.objects.all()
    authentication_classes = [TokenAuthentication]

"""النوع الرابع 
ViewSet
"""
class ViewSet_Depart(ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepSerializer

    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = ['pk','name']
    search_fields = ['name','floor']
    filterset_fields = ['name','floor']





@api_view(['GET'])
def find_dep(request):
    depart =Departments.objects.filter(
        name = request.data.get('name'))
    serializer = DepSerializer(depart,many=True)
    return Response(serializer.data)

