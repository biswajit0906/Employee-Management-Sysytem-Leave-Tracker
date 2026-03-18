from django.shortcuts import render, redirect,get_object_or_404
from .forms import RegisterForm, LoginForm, LeaveForm
from .models import Employee, Leave
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings


# REGISTER
def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            employee = form.save(commit=False)
            employee.user = user
            employee.save()

            # SEND EMAIL
            send_mail(
                'Registration Successful',
                'Welcome ! Your account created successfully .',
                settings.EMAIL_HOST_USER,
                [employee.email],
                fail_silently=False
            )

            return redirect('login')

    return render(request, 'register.html', {'form': form})


# EMPLOYEE LOGIN
def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('dashboard')

    return render(request, 'login.html', {'form': form})


# DASHBOARD
def dashboard(request):
    employee = Employee.objects.get(user=request.user)
    leaves = Leave.objects.filter(employee=employee)
    return render(request, 'dashboard.html', {'leaves': leaves})


# APPLY LEAVE
def apply_leave(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')   # or show error page

    form = LeaveForm()

    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.save()
            return redirect('dashboard')

    return render(request, 'apply_leave.html', {'form': form})

# ADMIN PANEL (SUPERUSER ONLY)
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')

    employees = Employee.objects.all()
    leaves = Leave.objects.all()

    # 🔥 COUNT LOGIC
    total_employees = employees.count()
    pending_count = Leave.objects.filter(status='Pending').count()
    approved_count = Leave.objects.filter(status='Approved').count()
    rejected_count = Leave.objects.filter(status='Rejected').count()

    return render(request, 'admin_dashboard.html', {
        'employees': employees,
        'leaves': leaves,
        'total_employees': total_employees,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    })


# APPROVE LEAVE
def approve_leave(request, id):
    leave = Leave.objects.get(id=id)
    leave.status = 'Approved'
    leave.save()
    return redirect('admin_dashboard')


# DELETE LEAVE
def delete_leave(request, id):
    leave = Leave.objects.get(id=id)
    leave.delete()
    return redirect('admin_dashboard')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


def update_leave_status(request, id):
    if not request.user.is_superuser:
        return redirect('login')

    leave = Leave.objects.get(id=id)
    status = request.POST.get('status')

    if status in ['Pending', 'Approved', 'Rejected']:
        leave.status = status
        leave.save()

        send_mail(
            'Leave Status Update',
            f'Your leave is {status}',
            settings.EMAIL_HOST_USER,
            [leave.employee.email],
            fail_silently=False
        )

    return redirect('admin_dashboard')



def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid admin credentials'})

    return render(request, 'admin_login.html')


def delete_employee(request, id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    emp = get_object_or_404(Employee, id=id)
    emp.delete()
    return redirect('admin_dashboard')


def update_employee(request, id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    emp = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        emp.name = request.POST.get('name')
        emp.email = request.POST.get('email')
        emp.department = request.POST.get('department')
        emp.contact = request.POST.get('contact')
        emp.save()
        return redirect('admin_dashboard')

    return render(request, 'update_employee.html', {'emp': emp})


def delete_leave(request, id):
    # 🔥 Only allow admin (superuser)
    if not request.user.is_superuser:
        return redirect('admin_dashboard')  # NOT login

    leave = get_object_or_404(Leave, id=id)
    leave.delete()

    return redirect('admin_dashboard')