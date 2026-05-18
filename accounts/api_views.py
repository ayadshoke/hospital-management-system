from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status,filters
from django_filters.rest_framework import DjangoFilterBackend

from departs.models import Departments,Doctors
from departs.serializer import DepSerializer
from doctors.serializer import DocSerializer
from .serializer import UserSerializer,PermSerializer
from django.contrib.auth.models import Permission
from .form import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


"""عرض واضافة بيانات اليوزرات"""
class UserList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        users = User.objects.all()
        serializer =UserSerializer(users,many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer = CustomUserCreationForm(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

"""تعديل بيانات اليوزر"""
class Edit_user(APIView):
    def get(self,request,id):
        item = User.objects.get(pk=id)
        serializer = UserSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request,id):
        item = User.objects.get(pk=id)
        serializer = UserSerializer(data=request.POST,instance=item)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class add_perm(APIView):
    def get(self,request,id):
        user = User.objects.get(pk=id)
        permissions = Permission.objects.all()
        serializer = PermSerializer(user.user_permissions,many=True)
        if request.method =='POST':
            codenames = request.POST.getlist('permission')
            perms = permissions.filter(codename__in=codenames)
            user.user_permissions.set(perms)

        # action = request.data['action']
        # if action == 'add':
        #     user.user_permissions.add(perm)
        # elif action == 'remove':
        #     user.user_permissions.clear()
        return Response(serializer.data)



"""
اول نوع من الدوال
رقم 1  Function Based View FBV
"""
@api_view(['GET','POST'])
def api_perm(request):
    if request.method=='GET':
        perm = Permission.objects.all().order_by('pk')
        serializer = PermSerializer(perm,many=True) #  ده بديل ال   form
        return Response(serializer.data,status=status.HTTP_200_OK)
    if request.method=='POST':
        serializer = PermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
def api_perm_detail(request,perm_id):
    try:
        item = Permission.objects.get(pk=perm_id)
    except Product.DoesNotExists:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method =='GET':
        serializer = PermSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method =='PUT':
        serializer = PermSerializer(item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data,{'message':'deleted'})
    if request.method == 'DELETE':
        item.delete()
        return Response({'message':'deleted'})


'''النوع الثاني
CLASS BASED VIEW
APIVIEW
'''
class View_Perm(APIView):
    def get(self,request):
        perm = Permission.objects.all().order_by('pk')
        serializer = PermSerializer(perm, many=True)  # ده بديل ال   form
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self,request):
        serializer = PermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class View_Perm_pk(APIView):
    def get(self,request,id):
        item = Permission.objects.get(pk=id)
        serializer = PermSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request,id):
        item = Permission.objects.get(pk=id)
        #الفرق بينها وبين html
        # انا استخدمت كلمة serializer بدل form واستخدمت request.dataبدل من request.POST
        # serializer = PermSerializer(item,request.data)
        # serializer = PermSerializer(item,data=request.data)
        serializer = PermSerializer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self,request,id):
        item = Permission.objects.get(pk=id)
        item.delete()
        return Response({'message': 'deleted'})

'''النوع الثالث
Generic views :
'''
class Gener_Perm(ListCreateAPIView):
    queryset = Permission.objects.all().order_by('pk')
    serializer_class = PermSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['id', 'name', 'codename']
    ordering_fields = ['pk', 'name', 'codename']
    search_fields = ['name', 'codename']

class Gener_Perm_pk(RetrieveUpdateDestroyAPIView): # دي بتعمل 3 حاجات
    queryset = Permission.objects.all()
    serializer_class = PermSerializer

'''النوع الرابع 
ViewSet
'''
class ViewSet_perm(ModelViewSet):
    queryset = Permission.objects.all().order_by('pk')
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    # filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    filterset_fields = ['id','name','codename'] #PermFilter هنا ربط ال filterset بدل name
    ordering_fields = ['pk','name','codename'] # دي خاص بالترتيب
    search_fields = ['name','codename'] # خاص بالبحث
    serializer_class = PermSerializer





#===============================================================================
# دي بتاعت الاقسام
class ViewSet_Depart(ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepSerializer

    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = ['pk','name']
    search_fields = ['name','floor']
    filterset_fields = ['name','floor']

class ViewSet_doc(ModelViewSet):
    queryset = Doctors.objects.filter(appointments__isnull=False).distinct().order_by('pk')
    serializer_class = DocSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['id', 'name', 'part']  # هنا لازم نكتب id وليس pk مهم
    ordering_fields = ['pk', 'name', 'part']
    search_fields = ['name', 'part', 'email']






