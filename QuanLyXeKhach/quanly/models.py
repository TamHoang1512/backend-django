
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VaiTro(models.Model):
    ten_vt = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ten_vt

    class Meta:
        ordering = ['id']


class User(AbstractUser):
    hinh_anh = models.ImageField(null=True, blank=True, upload_to='user/%Y/%m')
    so_dt = models.CharField(max_length=12, null=False, default=1)
    vai_tro = models.ForeignKey(VaiTro, on_delete=models.CASCADE, default=4, related_query_name='vaitro')

    def __str__(self):
        return self.username


class TuyenXe(ModelBase):
    ten_tuyen = models.CharField(max_length=200, null=False)
    diem_di = models.CharField(max_length=255, null=False)
    diem_den = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{0} - {1}".format(self.diem_di, self.diem_den)


def validate_date(value):
    if value <= timezone.now():
        raise ValidationError(
            _('Không nhập ngày giờ trong quá khứ'),
            params={'value': value},
        )


class ChuyenXe(ModelBase):
    ten_chuyenxe = models.CharField(max_length=255)
    tai_xe = models.ForeignKey(User, on_delete=models.CASCADE)
    khoi_hanh = models.DateTimeField(validators=[validate_date])
    tuyen_xe = models.ForeignKey(TuyenXe, null=True, on_delete=models.CASCADE, related_query_name='tuyen_xe')
    sl_ghe = models.SmallIntegerField()
    gia_ve = models.BigIntegerField(default=1)

    def __str__(self):
        return self.ten_chuyenxe

    def SoLuongVeHienTai(self):
        list_ve = self.ds_dat_ve.all()
        sl = 0
        for item in list_ve:
            sl += item.so_luong_ve
        return sl

    def SoLuongVeKhaDung(self):
        return self.sl_ghe - self.SoLuongVeHienTai()


def validate_gt0(value):
    if value <= 0:
        raise ValidationError(
            _('Nhập số vé dương'),
            params={'value': value},
        )


class DatVe(ModelBase):
    nguoi_dat = models.ForeignKey(User, on_delete=models.CASCADE)
    chuyen_xe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE,
                                  related_name='ds_dat_ve',
                                  related_query_name='chuyen_xe',
                                  )
    so_luong_ve = models.SmallIntegerField(validators=[validate_gt0], default=1)

    def __str__(self):
        return self.chuyen_xe.ten_chuyenxe

    def clean_fields(self, exclude=None):
        check = False
        try:
            if self.chuyen_xe:
                check = True
                if int(self.chuyen_xe.SoLuongVeKhaDung()) <= int(self.so_luong_ve):
                    check = False

        except:
            if check == False:
                raise ValidationError("Sai thông tin")
        # except:
        #     print('error')
        #     raise ValidationError("Khong co chuyen xe")


class Comment(ModelBase):
    noi_dung = models.TextField()
    chuyen_xe = models.ForeignKey(ChuyenXe,
                                  related_name='comments',
                                  on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.noi_dung


class ActionBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chuyenxe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chuyenxe')
        abstract = True


class Like(ActionBase):
    active = models.BooleanField(default=False)


class Rating(ActionBase):
    rate = models.SmallIntegerField(default=0)
