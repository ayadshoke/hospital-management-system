from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver


def keep_image(instance,filename):
    imagename ,extension = filename.split('.')
    return 'accounts/%s.%s'%(instance.username ,extension)

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=11)
    address =models.TextField(max_length=300 , blank=True ,null=True)
    image = models.ImageField(upload_to=keep_image,blank=True ,null=True,default='user_img.jpeg')
    slug = models.SlugField(blank=True, null=True)
    def save(self , *args , **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser,self).save(*args , **kwargs)


'''
user :
    proxy_models
    One-to-One field
    Extend abstract Base yser
    Extend abstract user
'''

'''
    username
    password
    first_name
    last_name
    email
'''
#  طريقة  one-to-one field
#settings.AUTH_USER_MODEL  دي بديل User علشان abstract
class Profile(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    jop = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.user)



@receiver(post_save,sender=settings.AUTH_USER_MODEL) # لو مش عامل abstract ها يبقي من User
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )