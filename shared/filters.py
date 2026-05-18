import django_filters
from django.contrib.auth.models import Permission


class PermFilter(django_filters.FilterSet):
    content_type = django_filters.ModelChoiceFilter(
        queryset = Permission.objects.values_list('content_type',flat=True).distinct())
    class Meta:
        model = Permission
        # fields = ['content_type']
        fields = '__all__'

#لحد لما اعمل تنزيل للمكتبة