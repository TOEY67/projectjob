from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.message[:50]}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รอดำเนินการ'),
        ('PROCESSING', 'กำลังดำเนินการ'),
        ('COMPLETED', 'เสร็จสิ้น'),
    ]

    order_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    image = models.ImageField(upload_to='order_images/', blank=True, null=True)
    custom_description = models.TextField(blank=True, null=True)
    custom_quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.order_id}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, "ไม่ทราบสถานะ")
    
class JewelryOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น'),
        ('shipped', 'จัดส่งแล้ว'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="order_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # ✅ เพิ่มสถานะ

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.get_status_display()})"
    
    class Product(models.Model):
        name = models.CharField(max_length=255)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        stock = models.IntegerField()

    def __str__(self):
        return self.name
    
from django.db import models

class TaskStatus(models.Model):
    task_name = models.CharField(max_length=255)  # ชื่อของขั้นตอนงาน
    is_completed = models.BooleanField(default=False)  # สถานะการทำงาน

    def __str__(self):
        return self.task_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg")
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username