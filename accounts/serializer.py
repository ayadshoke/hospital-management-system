from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import Permission,ContentType
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    perms = serializers.SerializerMethodField()
    perm_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['pk','username','first_name','last_name','email','phone','address',
                  'perm_count','perms']

    def get_perms(self,obj):
        perms = obj.user_permissions.all()
        perm_list =[]
        for perm in perms:
            perm_list.append(perm.codename)
        return perm_list
    def get_perm_count(self,obj):
        perm_count = obj.user_permissions.count()
        return perm_count



class PermSerializer(serializers.ModelSerializer):
    # هنا في انا بضيف اعمدة اضافية
    app_label= serializers.SerializerMethodField() # دي الاسماء اللي ها تظهر
    model_name= serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

     # ده علشان اعمل لسته اختار منها في المتصفح
    content_type = serializers.SlugRelatedField(queryset=ContentType.objects.all(),slug_field='model',write_only=True)

    class Meta:
        model = Permission
        ordering = ['pk']
        # fields = '__all__' # دول طريقتين
        fields = ('id','name','codename','app_label','content_type','model_name','user_count','users')
    # هنا بوضح الاعمدة دي هاتجيب بيانات من فين في كل كائن
    def get_app_label(self,obj): # دي علشان ارجع اسم app في المتصفح
        app_label = obj.content_type.app_label
        return app_label #بجيب من الموديل
    def get_model_name(self,obj):# ودي علشان ارجع اسم model زي في html لما كنت بعمل perm.content.id.model
        return obj.content_type.model
    def get_users(self,obj):
        username = []
        for user in obj.user_set.all():  # علشان العلاقة many_to_many
            if user.is_superuser:
                return 'superuser'
            username.append(user.username)
            return username
    def get_user_count(self,obj):
        user_count = obj.user_set.count()
        return user_count

