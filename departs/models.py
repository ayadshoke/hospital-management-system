from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
user = get_user_model()


class Departments(models.Model):
    specialization = [('1','children'),('2','interior'),('3','bones'),('4','the heart'),
                      ('5','eyes'),('6','nose'),('7','women'),('8','utensils'),('9','surgery'),('10','tract')]
    floors = [('1','First'),('2','Second'),('3','Third'),('4','Fourth'),('5','Fifth'),('6','Sixth'),('7','Seventh'),('8','Eighth'),('9','Ninth'),('10','Tenth')]

    name = models.CharField(max_length=200,choices = specialization,unique=True)
    floor = models.CharField(max_length=20,choices=floors)
    phone = models.CharField(max_length=11 , unique=True)
    slug = models.SlugField(blank=True,null=True)

    def save(self,*args ,**kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = str(self.pk)
            super().save(update_fields=['slug'])

    def __str__(self):
        return self.get_name_display()
    class Meta :
        ordering = ['pk']


class Patients(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    area = models.CharField(max_length=150,blank=True ,null=True)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Patients'
        permissions = [('can_view_patient','can_view_patient'),('can_add_patient','can_add_patient'),
                       ('can_edit_patient','can_edit_patient'),('can_delete_patient','can_delete_patient')]
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = str(self.pk)
            super().save(update_fields=['slug'])



class Doctors(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    part = models.ForeignKey(Departments, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11,unique=True)
    email= models.EmailField(max_length=200,unique=True)
    address = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Doctors'
        unique_together = [('name','part')]
    def __str__(self):
        return f"{self.name}"

    # def clean(self):
    #     existing = Doctors.objects.filter(doc_name=self.doc_name,day=self.day).exclude(pk=self.pk).first()
    #     if existing and existing.part != self.part:
    #         raise ValidationError('No')

    def save(self,*args ,**kwargs):
        # self.clean()
        existing = Doctors.objects.filter(name=self.name).exclude(pk=self.pk).last()
        if existing:
            self.phone = existing.phone
            self.email = existing.email
            self.part=existing.part
        super().save(*args,**kwargs)


class Appointments(models.Model):
    list = [('1','normal'),('2','urgent'),('3','consultation')]
    detect_stat = [('1','OnGoing'),('2','Completed'),('3','Cancelled')]

    patient = models.ForeignKey(Patients,on_delete= models.CASCADE)
    doctor = models.ForeignKey(Doctors,on_delete= models.DO_NOTHING, blank=True, null=True)
    detect = models.CharField(max_length=50,choices=list,default='normal')#الكشف
    detect_value = models.DecimalField(max_digits=6 , decimal_places=2)
    employee = models.ForeignKey(user,on_delete= models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    paid_stat = models.BooleanField(max_length=10,default=False)
    status = models.CharField(max_length=50,choices=detect_stat)
    slug = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = str(self.pk)
            super().save(update_fields=['slug'])

    def __str__(self):
        return f"{self.slug} / {self.patient} / {self.created_at}"
    class Meta:
        ordering = ['created_at']
        # unique_together = [('patient', 'created_at')]

    @property
    def is_completed(self):
        return self.filter(status='Completed').count()


class Area(models.Model):
    my_city = [('Cairo','Cairo'), ('Alexandria','Alexandria'), ('Aswan','Aswan'), ('Luxor','Luxor')]
    code = models.IntegerField()
    name = models.CharField(max_length=200,choices=my_city)
    def __str__(self):
        return self.get_name_display()
    class Meta:
        ordering = ['code']


class Days(models.Model):
    days = [('1','saturday'), ('2','sunday'), ('3','monday'), ('4','tuesday'),
            ('5','wednesday'), ('6','thursday'), ('0','friday')]
    day = models.CharField(max_length=20,choices=days)
    available = models.BooleanField(default=True)
    doctor = models.ForeignKey(Doctors,on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return self.get_day_display()
    class Meta:
        ordering = ['day']
        unique_together = [('day','doctor')]

class Payment(models.Model):
    payment_type = [('1','cash'),('2','visa'),('3','cheque'),('4','bank')]

    appoint = models.ForeignKey(Appointments,on_delete=models.CASCADE)
    paid_type = models.CharField(max_length=30,choices=payment_type,default='1')
    paid_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=6 , decimal_places=2)

    def __str__(self):
        return f"{self.paid_date} / {self.amount}"
    class Meta:
        ordering = ['paid_date']



