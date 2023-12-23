from typing import Any
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.generic.base import View
from django.core.paginator import Paginator
from django.db.models import Count

import os
import datetime
import asyncio
from django.http import HttpResponse, Http404

from messdeck import settings
from .MenuToJSON import MenuParser
from .models import Dish, Rating, Complaint, AttendanceRecord, MyUser, Menu, MenuDishEntry
from openpyxl import Workbook

# Create your views here.

class MenuDisplay:
    
    def __init__(self, date, breakfast, lunch, dinner, has_rated) -> None:
        self.breakfast = breakfast
        self.date = date
        self.lunch = lunch
        self.dinner = dinner
        self.has_rated = has_rated

def student_profile_view(request):
    context = {
        'name' : request.user.Name,
        'id_number' : request.user.BITS_ID,
        'hostel'  : "ABC Hostel"
    }
    
    return render(request, "deck/MainWebsite/student_profile.html", context)

def staff_profile_view(request):
    context = {
        'name' : request.user.Name,
        'psrn_number' : request.user.PSRN_No,
    }
    
    return render(request, "deck/MainWebsite/staff_profile.html", context)


async def save_parsed_menu():
    await Menu.objects.all().adelete()
    menu_dict : dict = MenuParser().create_menu_structure()
    
    for d in menu_dict.keys():
        date_components = d.split('-')
        year = int(date_components[0])
        month = int(date_components[1])
        day = int(date_components[2])
        new_date = datetime.date(year, month, day)
        
        new_menu_object = Menu(date=new_date)
        await new_menu_object.asave()
        
        breakfast_list = menu_dict[d]['BREAKFAST']
        lunch_list = menu_dict[d]['LUNCH']
        dinner_list = menu_dict[d]['DINNER']
        
        for dish in breakfast_list:
            new_dish = MenuDishEntry(name=dish, meal='B', menu_object=new_menu_object)
            await new_dish.asave()
            
        for dish in lunch_list:
            new_dish = MenuDishEntry(name=dish, meal='L', menu_object=new_menu_object)
            await new_dish.asave()
            
        for dish in dinner_list:
            new_dish = MenuDishEntry(name=dish, meal='D', menu_object=new_menu_object)
            await new_dish.asave()
        
    await asyncio.sleep(5)
    print("COMPLETE")


def update_menu_view(request):
    context = {'post' : False}
    
    if(request.method == 'POST'):
        uploaded_file = request.FILES.get('menu_file')
        print(type(uploaded_file))
        system = FileSystemStorage()
        system.delete('MessMenu.xlsx')
        
        system.save("MessMenu.xlsx", uploaded_file)
        
        asyncio.run(save_parsed_menu())
        
        context['post'] = True
        
    return render(request, "deck/MainWebsite/menu_update_form.html", context)

def login_page(request):
    context = {}
    if(request.user.is_authenticated):
        if(request.user.socialaccount_set.exists()):
            return HttpResponseRedirect(reverse('student_dashboard'))
        else:
            return HttpResponseRedirect(reverse('staff_dashboard'))
    
    return render(request, "deck/LoginScreen/index.html", context)

def menu_view(request):
    context = {}
    if(request.method == 'POST'):
        ratings : dict = dict(request.POST)
        ratings.pop('csrfmiddlewaretoken')
        date_components = request.POST['dateInput'].split('-')
        date_of_rating = datetime.date(int(date_components[0]), int(date_components[1]), int(date_components[2]))
        ratings.pop('dateInput')
        if(not Rating.objects.filter(user=request.user, date=date_of_rating).exists()):
            for dish_name in ratings.keys():
                dish_object = Dish.objects.get_or_create(dish=dish_name)
                rating = Rating(user=request.user, dish=dish_object[0], rating=int(ratings[dish_name][0]), date=date_of_rating)
                rating.save()
    
    
    if(Menu.objects.all().count() > 0):
        
        menu_objects = []
        
        breakfast_lengths = []
        lunch_lengths = []
        dinner_lengths = []
        
        for k in Menu.objects.all().order_by("date"):
            breakfast_dishes = list(k.menudishentry_set.filter(meal='B').values_list('name', flat=True))
            lunch_dishes = list(k.menudishentry_set.filter(meal='L').values_list('name', flat=True))
            dinner_dishes = list(k.menudishentry_set.filter(meal='D').values_list('name', flat=True))
            
            breakfast_lengths.append(len(breakfast_dishes))
            lunch_lengths.append(len(lunch_dishes))
            dinner_lengths.append(len(dinner_dishes))
            
            obj = MenuDisplay(k.date, breakfast_dishes, lunch_dishes, dinner_dishes, Rating.objects.filter(user=request.user, date=k.date).exists())
            menu_objects.append(obj)

        
        breakfast_rows = max(breakfast_lengths) + 1
        lunch_rows = max(lunch_lengths) + 1
        dinner_rows = max(dinner_lengths) + 1
        number_of_dates = len(menu_objects)
        
        breakfast_display_rows = [[''] * number_of_dates for i in range(breakfast_rows)]
        
        for i, obj in enumerate(menu_objects):
            populated_rows = len(obj.breakfast)
            for j, item in enumerate(obj.breakfast):
                breakfast_display_rows[j][i] = item
        
        lunch_display_rows = [[''] * number_of_dates for i in range(lunch_rows)]
        
        for i, obj in enumerate(menu_objects):
            populated_rows = len(obj.lunch)
            for j, item in enumerate(obj.lunch):
                lunch_display_rows[j][i] = item
                
        dinner_display_rows = [[''] * number_of_dates for i in range(dinner_rows)]
        
        for i, obj in enumerate(menu_objects):
            populated_rows = len(obj.dinner)
            for j, item in enumerate(obj.dinner):
                dinner_display_rows[j][i] = item
                    
        
        context = {'menu_objects' : menu_objects}
        context['breakfast_rows'] = breakfast_display_rows
        context['lunch_rows'] = lunch_display_rows
        context['dinner_rows'] = dinner_display_rows
        
        
    return render(request, "deck/MainWebsite/mess_menu.html", context)


def complain_view(request):
    context = {'post' : False }
    
    if(request.method == 'POST'):
        details : dict = dict(request.POST)
        new_id = None
        if(Complaint.objects.exists()):
            new_id = Complaint.objects.order_by('-complaint_id').first().complaint_id + 1
        else:
            new_id = 1
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES.get('image')
        print(image)
        new_complaint = Complaint(complaint_id=new_id, title=title, description=description, image=image, student=request.user)
        new_complaint.save()
        context['post'] = True
    
    return render(request, "deck/MainWebsite/complaint_form.html", context)



class ComplaintsView(View):
    
    def get(self, request, *args, **kwargs):
        get_request : dict = request.GET
        page_no = get_request.get('page', None)
        
        if(page_no == None):
            page_no = 1
        else:
            page_no = int(page_no)
        
        paginator = Paginator(Complaint.objects.all().order_by("-complaint_id"), 10)
        object_list = paginator.get_page(page_no)
        context = {}
        context['complaints'] = object_list
        context['pages'] = paginator.get_elided_page_range(page_no, on_each_side=1, on_ends=1)
        context['last_page'] = (page_no == paginator.num_pages)
        context['first_page'] = (page_no == 1)
        context['page_no'] = page_no
    
        return render(request, "deck/MainWebsite/complaint_list.html", context)
        


class RatingDisplay:
    
    def __init__(self, name, rating_count, average_rating) -> None:
        self.name = name
        self.rating_count = rating_count
        self.average_rating = average_rating

def ratings_view(request):
    context = {}
    object_list = []
    for dish in Dish.objects.all():
        rating_count = dish.rating_set.count()
        sum = 0
        for rating in dish.rating_set.all():
            sum += rating.rating

        average_rating = None
        if(rating_count != 0):
            average_rating = sum / rating_count
        else:
            average_rating = "Not Yet Rated"
        
        rating_display_object = RatingDisplay(dish.dish, rating_count, average_rating)
        object_list.append(rating_display_object)
    
    context['rating_objects'] = object_list
    
    return render(request, "deck/MainWebsite/ratings_list.html", context)
        

class AttendanceDisplay:
    
    def __init__(self, date, breakfast_count, lunch_count, dinner_count) -> None:
        self.date = date
        self.breakfast_count = breakfast_count
        self.lunch_count = lunch_count
        self.dinner_count = dinner_count



def attendance_history_view(request):
    context = {}
    list_of_rows = []
    for x in range(0, 6):
        date_to_check = datetime.date.today() - datetime.timedelta(days=x)
        breakfast_count = AttendanceRecord.objects.filter(date=date_to_check, meal_type=1).count()
        lunch_count = AttendanceRecord.objects.filter(date=date_to_check, meal_type=2).count()
        dinner_count = AttendanceRecord.objects.filter(date=date_to_check, meal_type=3).count()
        row_object = AttendanceDisplay(date_to_check, breakfast_count, lunch_count, dinner_count)
        list_of_rows.append(row_object)
        
    context['attendance_rows'] = list_of_rows
    
    return render(request, "deck/MainWebsite/attendance_history.html", context)

class BillDisplay:
    
    def __init__(self, name, breakfast_count, lunch_count, dinner_count, total) -> None:
        self.name = name
        self.breakfast_count = breakfast_count
        self.lunch_count = lunch_count
        self.dinner_count = dinner_count
        self.total = total

def bills_view(request):
    context = {'post' : False}
    row_objects_list = []
    
    for user in MyUser.objects.all():
        if(user.socialaccount_set.exists()):
            attendance_markers = user.attendancerecord_set.all()
            breakfast_count = user.attendancerecord_set.filter(meal_type=1).count()
            lunch_count = user.attendancerecord_set.filter(meal_type=2).count()
            dinner_count = user.attendancerecord_set.filter(meal_type=3).count()
            
            total_cost = breakfast_count * 80 + lunch_count * 180 + dinner_count * 150
            
            row_object = BillDisplay(user.Name, breakfast_count, lunch_count, dinner_count, total_cost)
            row_objects_list.append(row_object)
    
    context['billing_data'] = row_objects_list
    
    if(request.method == 'POST'):
        workbook = Workbook()
        ws = workbook.active
        
        column_names = ['Name', 'Breakfast Count', 'Lunch Count', 'Dinner Count', 'Total Bill']
        
        ws.append(column_names)
        
        context['post'] = True
        
        for row in row_objects_list:
            row_list = []
            row_list.append(row.name)
            row_list.append(row.breakfast_count)
            row_list.append(row.lunch_count)
            row_list.append(row.dinner_count)
            row_list.append(row.total)
            
            ws.append(row_list)
        
        file_path = str(settings.MEDIA_ROOT) + '\Bill.xlsx'
        workbook.save(file_path)
        
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
        
    return render(request, "deck/MainWebsite/bills_calculation.html", context)


def bills_download_view(request):
    pass


def student_dashboard_view(request):
    context = {'attendance' : 0, 'next_meal_found' : False, 'attendance_given' : False}
    
    if(request.method == 'POST'):
        meal_type = request.POST['meal_type']
        if(not AttendanceRecord.objects.filter(user=request.user, meal_type=meal_type, date=datetime.date.today()).exists()):
            new_attendance = AttendanceRecord(user=request.user, meal_type=meal_type)
            new_attendance.save()
    

    if(datetime.datetime.now().hour >= 7 and datetime.datetime.now().hour < 16):
        context['attendance'] = 1
    elif(datetime.datetime.now().hour >= 12 and datetime.datetime.now().hour < 14):
        context['attendance'] = 2
    elif(datetime.datetime.now().hour >= 19 and datetime.datetime.now().hour < 21):
        context['attendance'] = 3
    
    context['attendance_given'] = AttendanceRecord.objects.filter(user=request.user, meal_type=context['attendance'], date=datetime.date.today()).exists()

    menu_structure : dict = MenuParser().create_menu_structure()
    
    desired_date = datetime.date.today()
    if(datetime.datetime.now().hour >= 21):
        desired_date = desired_date + datetime.timedelta(days=1)
    desired_meal = None
    
    if(datetime.datetime.now().hour >= 21 or datetime.datetime.now().hour < 9):
        desired_meal = 'BREAKFAST'
    elif(datetime.datetime.now().hour >= 9 and datetime.datetime.now().hour < 14):
        desired_meal = 'LUNCH'
    elif(datetime.datetime.now().hour >= 14 and datetime.datetime.now().hour < 21):
        desired_meal = 'DINNER'
    
    context['next_meal_name'] = desired_meal
    
    for k in menu_structure.keys():
        date_components = k.split('-')
        date_of_data = datetime.date(int(date_components[0]), int(date_components[1]), int(date_components[2]))
        if(date_of_data == desired_date):
            context['next_meal_found'] = True
            context['meal_data'] = list(Menu.objects.get(date=date_of_data).menudishentry_set.list_values("name", flat=True))
            
    return render(request, "deck/MainWebsite/student_dashboard.html", context)



def home_redirect(request):
    print(request.GET.get('next'))
    
    home_page = None
    if(request.user.socialaccount_set.exists()):
        home_page = reverse('student_dashboard')
    else:
        home_page = reverse('staff_profile')
    
    return HttpResponseRedirect(home_page)
