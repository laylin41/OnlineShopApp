# Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the TABLE in the database
# Feel free to rename the models, but DON'T rename db_table values or field names.
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify

class Categories(models.Model):
    category_id = models.AutoField(db_column='Category_ID', primary_key=True) 
    category_name = models.CharField(db_column='Category_Name', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"Category: {self.category_name}"


class Droppoints(models.Model):
    droppoint_id = models.AutoField(db_column='Droppoint_ID', primary_key=True)
    adress_name = models.CharField(db_column='Adress_name', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Droppoints'
        verbose_name_plural = 'Droppoints'

    def __str__(self):
        return f"Droppoint: {self.adress_name}"


class Goods(models.Model):
    good_id = models.AutoField(db_column='Good_ID', primary_key=True)  
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, db_column='Category_ID', blank=True, null=True)
    name = models.CharField(db_column='Name', blank=True, null=True)  
    slug = models.SlugField(db_column='Slug', blank=True, null=True) 
    price = models.FloatField(db_column='Price', blank=True, null=True) 
    discount = models.IntegerField(db_column='Discount', blank=True, null=True)  
    description = models.TextField(db_column='Description', blank=True, null=True)  
    characteristics = models.TextField(db_column='Characteristics', blank=True, null=True) 
    rating = models.FloatField(db_column='Rating', blank=True, null=True) 
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)

    @property
    def discounted_price(self):
        if self.discount:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    @property
    def average_rating(self):
        return self.reviews_set.aggregate(avg=Avg('rating'))['avg'] or 0

    class Meta:
        managed = False
        db_table = 'Goods'
        verbose_name_plural = 'Goods'

    def save(self, *args, **kwargs):
        # Automatically generate slug from name if slug is not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Good: {self.name} (ID: {self.good_id})"
    
class GoodImage(models.Model):
    goodimage_id = models.AutoField(db_column='GoodImage_ID', primary_key=True)
    good = models.ForeignKey('Goods', on_delete=models.CASCADE, db_column='Good_ID', blank=True, null=True)
    image = models.ImageField(db_column='Image', upload_to='goods_images/', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GoodImage'
        verbose_name_plural = 'GoodImages'

    def __str__(self):
        return f"Image for {self.good.name}"


class Ordergood(models.Model):
    ordergood_id = models.AutoField(db_column='OrderGood_ID', primary_key=True)  
    order = models.ForeignKey('Orders', models.CASCADE, db_column='Order_ID')  
    good = models.ForeignKey('Goods', models.SET_NULL, db_column='Good_ID', null=True)
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OrderGood'
        unique_together = (('order', 'good'),)
        verbose_name_plural = 'OrderGood'
    
    def __str__(self):
        return f"OrderGood: {self.good.name} x {self.quantity}"


class Orders(models.Model):
    order_id = models.AutoField(db_column='Order_ID', primary_key=True)  
    status = models.CharField(db_column='Status', blank=True, null=True) 
    date_order_confirmed = models.DateField(db_column='Date_order_confirmed', blank=True, null=True) 
    delivery_code = models.CharField(db_column='Delivery_code', blank=True, null=True) 
    date_delivered = models.DateField(db_column='Date_delivered', blank=True, null=True)  
    delivery_adress_custom = models.CharField(db_column='Delivery_Adress_Custom', blank=True, null=True)  
    userprofile = models.ForeignKey('Userprofiles', models.DO_NOTHING, db_column='UserProfile_ID', blank=True, null=True)  
    droppoint = models.ForeignKey('Droppoints', models.SET_NULL, db_column='Droppoint_ID', blank=True, null=True) 
    goods = models.ManyToManyField('Goods', through='Ordergood', related_name='orders')

    class Meta:
        managed = False
        db_table = 'Orders'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order ID: {self.order_id} - Status: {self.status}"


class Reviews(models.Model):
    review_id = models.AutoField(db_column='Review_ID', primary_key=True)  
    rating = models.FloatField(db_column='Rating', blank=True, null=True)  
    comment = models.TextField(db_column='Comment', blank=True, null=True) 
    good = models.ForeignKey('Goods', models.CASCADE, db_column='Good_ID', blank=True, null=True)  
    userprofile = models.ForeignKey('Userprofiles', models.SET_NULL, db_column='UserProfile_ID', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'Reviews'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"Review {self.review_id} for {self.good.name} - Rating: {self.rating}"


class Userprofiles(models.Model):
    profile_id = models.AutoField(db_column='Profile_ID', primary_key=True)  
    authuser = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='AuthUser_ID', blank=True, null=True)  
    phone_number = models.CharField(db_column='Phone_number', blank=True, null=True)  
    base_delivery_adress = models.CharField(db_column='Base_delivery_adress', blank=True, null=True) 
    display_name = models.CharField(db_column='Display_name', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'UserProfiles'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        return f"UserProfile - Username: {self.authuser.username} (AuthUser_ID:{self.profile_id})"


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

    def __str__(self):
        return f"AuthUser: {self.username} (ID:{self.id})"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
