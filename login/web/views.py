from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib.auth.models import User  
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import ChatMessage, User
from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist



def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data['role']

            if role == 'staff':
                user.is_staff = True
            else:
                user.is_staff = False

            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ใช้ is_staff ในการแยกบทบาท
            if user.is_staff:
                return redirect('admin_dashboard')  # หากเป็น staff/admin
            else:
                return redirect('home')  # หากเป็น user ทั่วไป
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page

@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        user.email = request.POST.get("email", user.email)
        user.save()  # บันทึกอีเมลของ user

        dob_str = request.POST.get("dob", None)

        # ตรวจสอบว่าผู้ใช้มี `UserProfile` หรือไม่ ถ้าไม่มีให้สร้างใหม่
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.name = request.POST.get("name", profile.name)
        profile.address = request.POST.get("address", profile.address)
        profile.dob = request.POST.get("dob", profile.dob)
        profile.phone = request.POST.get("phone", profile.phone)

        # ตรวจสอบว่ามีการอัปโหลดรูปภาพหรือไม่
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()  # บันทึกข้อมูล UserProfile
        return redirect("profile")  # โหลดหน้า Profile ใหม่

    return render(request, "profile.html", {"user": request.user})

def profileedit_view(request):
    return render(request, 'profileedit.html')

@login_required
def status_view(request, order_id):
    if not request.user.is_staff:
        return redirect('home')  # ป้องกันไม่ให้ User ทั่วไปเข้าถึง

    order = get_object_or_404(JewelryOrder, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JewelryOrder.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, "✅ อัปเดตสถานะเรียบร้อย!")
        else:
            messages.error(request, "⚠️ สถานะไม่ถูกต้อง")

        return redirect('admin_dashboard')  # ✅ กลับไปที่แดชบอร์ด

    return render(request, 'status.html', {'order': order})


@login_required
def chat_view(request, user_id):
    other_user = User.objects.get(id=user_id)
    messages = ChatMessage.objects.filter(
        sender=request.user, receiver=other_user
    ) | ChatMessage.objects.filter(
        sender=other_user, receiver=request.user
    )
    messages = messages.order_by("timestamp")  # เรียงตามเวลาส่งข้อความ

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                message=message_text
            )
            return redirect('chat', user_id=other_user.id)  # รีเฟรชหน้าแชทหลังส่งข้อความ

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def chat_list(request):
    if request.user.is_staff:  # ถ้าเป็นแอดมิน ดูได้ทุกข้อความ
        messages = ChatMessage.objects.all().order_by('-timestamp')
    else:  # ถ้าเป็นผู้ใช้ทั่วไป ดูเฉพาะข้อความที่เกี่ยวข้องกับตัวเอง
        messages = ChatMessage.objects.filter(receiver=request.user).order_by('-timestamp')

    return render(request, "chat_list.html", {"messages": messages})

@require_POST
def upload_image(request, id):
    order = get_object_or_404(Order, pk=id)
    form = UploadImageForm(request.POST, request.FILES)

    if form.is_valid():
        image = form.cleaned_data['image']
        order.image = image
        order.save()
        messages.success(request, 'อัปโหลดรูปภาพสำเร็จแล้ว!')
    else:
        messages.error(request, 'เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ')

    return redirect(reverse('order_detail', args=[id]))

@require_POST
def customize_product(request, id):
    order = get_object_or_404(Order, pk=id)
    description = request.POST.get('description', '')
    quantity = request.POST.get('quantity', 1)

    if description.strip() == '':
        messages.error(request, 'กรุณาระบุรายละเอียดสินค้า')
    else:
        order.custom_description = description
        order.custom_quantity = quantity
        order.save()
        messages.success(request, 'สั่งทำสินค้าสำเร็จแล้ว!')

    return redirect(reverse('order_detail', args=[id]))

@login_required
def create_order(request):
    """
    สั่งทำจิวเวลรี่
    """
    if request.method == 'POST':
        form = JewelryOrderForm(request.POST, request.FILES)  # ✅ รองรับการอัปโหลดไฟล์
        if form.is_valid():
            order = form.save(commit=False)  # ✅ ยังไม่บันทึกลง DB จนกว่าจะแก้ไขค่า user
            order.user = request.user  # ✅ กำหนด user ที่ทำรายการสั่งซื้อ
            order.save()  # ✅ บันทึกลงฐานข้อมูล

            messages.success(request, "สั่งทำจิวเวลรี่สำเร็จ! กรุณารอการดำเนินการ")
            return redirect(reverse('order_success'))  # ✅ ใช้ reverse() เพื่อให้ Django จัดการ URL

        else:
            messages.error(request, "กรุณากรอกข้อมูลให้ถูกต้อง!")

    else:
        form = JewelryOrderForm()

    return render(request, 'book_appointment.html', {'form': form})

def order_success(request):
    return render(request, 'order_success.html')

# ✅ หน้า Dashboard
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')  # ป้องกันไม่ให้ User ทั่วไปเข้าถึง

    # ✅ ดึงรายการคำสั่งซื้อทั้งหมด
    orders = JewelryOrder.objects.all().order_by('-created_at')

    return render(request, 'admin_dashboard.html', {'orders': orders})

@login_required
def admin_chat_room(request):
    if not request.user.is_staff:
        return redirect('home')  # ถ้าไม่ใช่แอดมิน ส่งกลับหน้าแรก
    
    # ดึงรายชื่อผู้ใช้ที่ไม่ใช่แอดมิน
    users = User.objects.filter(is_staff=False)

    return render(request, "admin_chat_room.html", {"users": users})


def order_history_view(request):
    orders = JewelryOrder.objects.all().order_by('-created_at')
    return render(request, 'Admin_Order_History.html', {'orders': orders})

def delete_order(request, order_id):
    order = get_object_or_404(JewelryOrder, id=order_id)
    order.delete()
    return redirect('Admin_Order_History')

# ✅ ออกจากระบบ
def admin_logout(request):
    logout(request)
    return redirect('login')  # หลังจาก logout จะไปที่หน้า login

@login_required
def task_list_view(request):
    """
    แสดงรายการคำสั่งซื้อของผู้ใช้ที่ล็อกอินอยู่
    """
    orders = JewelryOrder.objects.filter(user=request.user).order_by('-created_at')  # ✅ ดึงเฉพาะของ user ปัจจุบัน
    return render(request, 'task_list.html', {'orders': orders})


def update_view(request):
    # ดึงคำสั่งซื้อทั้งหมดจากฐานข้อมูล
    orders = JewelryOrder.objects.all()  # ดึงทุกคำสั่งซื้อ
    if request.method == 'POST':
        order_id = request.POST.get('order-id')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        try:
            order = JewelryOrder.objects.get(id=order_id)
        except Order.DoesNotExist:
            return render(request, 'error_page.html', {'message': 'ไม่พบคำสั่งซื้อตามที่ระบุ'})

        # อัพเดตข้อมูลคำสั่งซื้อ
        order.status = status
        order.notes = notes
        order.save()

        return redirect('update_success')  # เปลี่ยนเส้นทางไปที่หน้าสำเร็จ

    # ส่งคำสั่งซื้อทั้งหมดไปยังเทมเพลต
    return render(request, 'update.html', {'orders': orders})


def update_success(request):
    return render(request, 'update_success.html')