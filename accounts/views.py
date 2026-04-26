from django.shortcuts import render,redirect
from .models import RegUser
from django.contrib import messages

def HomePage(request):
    return render(request, 'accounts/home.html')

#================================================================================================

def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = RegUser.objects.get(username=username, password=password)
            if user.status == 'active':
                return redirect('userhome')
            else:
                messages.success(request, 'Wait for admin to activate your account')
        except RegUser.DoesNotExist:
            messages.success(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

#================================================================================================

def adminhome(request):
    return render(request, 'accounts/adminbase.html')

#---------------------------------------------------------------------------------------------------

def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin' and password== 'admin':
            return render(request, 'accounts/adminbase.html')
        else:
            return render(request, 'accounts/adminlogin.html')
    return render(request, 'accounts/adminlogin.html')  

#----------------------------------------------------------------------------------------------------

def register_user(request):
    print("Request method is", request.method)
    if request.method == 'POST':
        print("Request method is POST")
        full_name = request.POST.get('fullName')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone')
        try:
            if full_name and username and email and password and phone_number :
                new_user = RegUser(
                    full_name=full_name,
                    username=username,
                    email=email,
                    password=password,
                    phone_number=phone_number,
                    status='waiting'
                )
                new_user.save()
                messages.success(request, 'User registered successfully.')
                return redirect('register')
            else:
                print('error at register')
                messages.success(request,'User not Registered Successfully')
        except Exception as e:
              print(f'the exception is {e}')
              messages.success(request,f'error at register is {str(e)}')      
    return render(request,'accounts/register.html')

#------------------------------------------------------------------------------------------------------

def view_user(request):
    users = RegUser.objects.all()
    return render(request,'accounts/viewuser.html',{'users':users})

#----------------------------------------------------------------------------------------------------------

def activate_user(request,id):
    user = RegUser.objects.get(id=id)
    user.status = 'active'
    user.save()
    return redirect('viewuser')

#---------------------------------------------------------------------------------------------------------

def block_user(request,id):
    user=RegUser.objects.get(id=id)
    user.status = 'waiting'
    user.save()
    return redirect('viewuser')

    