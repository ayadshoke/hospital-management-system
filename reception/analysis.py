from sqlalchemy import create_engine
import os
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from departs.models import Appointments


def analysis_appoint(request):
    qs = Appointments.objects.filter(paid_stat=True).values()
    data =pd.DataFrame(qs) # دي علشان التحليل
    df = pd.DataFrame(list(qs))# دي علشان العرض في html
    # df = df.to_html(classes ='table table-bordered',index=False)# دي جدول جاهز زي الاكسيل بالظبط
    df = df.to_dict(orient='records')#دي انت اللي بتعمل الجدول في html
    ##   حساب اكبر قيمة
    max = data['detect_value'].max()
    # max1 = data.max() # هنا بنرجع الصف صاحب اعلي قيمة او معرفة الشخص اللي دفع اعلي قيمة
    name_max = data.loc[data['detect_value'].idxmax(),'patient_id']# معرفة الشخص صاحب اعلي قيمة
    max_row = data.max(axis=0)# اعي قيمة في الصفوف
    # max_column = data.max(axis=1) # اعلي قيمة في الاعمده
    ##   حساب اضغر قيمة
    min = data['detect_value'].min()
    name_min = data.loc[data['detect_value'].idxmin(),'patient_id']
    min_row = data.min(axis=0)

    # جلب صفوف معينة
    head = data.head(2).to_html() # دي بتاخد من اول الجدول
    # head = data.head(len(data)).to_html() # دي لعرض كل الصفوف

    # tail = data.tail().to_html() # دي اخر5 صفوف
    tail = data.tail(2).to_html() # دي اخر5 صفوف

    # المتوسط
    avar =data['detect_value'].mean() # متوسط كل القيم
    # avar =data.mean(skipna=True) #لتجاهل القيم الفارغة

    #اضافة عامود محسوب
    data['tax']= 0.25
    data['elkhasm']=data['tax'] * data['detect_value'].astype('float')# دي لتحويل ال decimal الي float
    table = data.to_html(classes ='table table-bordered',index=False)


    context ={'data':df,'max':max,'min':min,'max_row':max_row,'name_max':name_max,'name_min':name_min,
              'min_row':min_row,'head':head,'tail':tail,'avar':avar,'table':table}
    return render(request,'analysis.html',context)

def load_appoint_csv(request):
    qs = Appointments.objects.all().values()
    df = pd.DataFrame(list(qs))
    response = HttpResponse(content_type='text/csv')
    response['content_Disposition']='attachment;filename=appoint.csv',df.to_csv(response,index=False)
    return response

def load_appoint_excel(request):
    qs = Appointments.objects.all().values()
    df = pd.DataFrame(list(qs))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['content_Disposition']='attachment;filename=appoint.xlsx',df.to_excel(response,index=False)
    return response



def read_excel(request):
    file_path = "C:/Users/Ctrl-Halim/Desktop/target.xlsx"
    new_data = pd.read_excel(file_path)
    # print(os.path.exists("C:/Users/Ctrl-Halim/Desktop/target.xlsx"))
    df = new_data.to_html(classes ='table table-bordered',index=False)

    context ={'excel':df}
    return render(request, 'excel.html', context)

def save_data(request):
    file_path = "C:/Users/Ctrl-Halim/Desktop/target.xlsx"
    new_data = pd.read_excel(file_path)
    engine = create_engine("mysql+mysqldb://root:12345@localhost/clinic")

    new_data.to_sql(
        name='target',  # اسم الجدول
        con=engine,
        if_exists='append',  # replace = يمسح ويعيد إنشاء الجدول
        index=False)
    return HttpResponse('تم الحفظ بنجاح ')
