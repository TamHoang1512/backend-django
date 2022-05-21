from datetime import datetime
from django.contrib import admin
from .models import User, TuyenXe, ChuyenXe, DatVe, VaiTro
from django.urls import path
from django.utils.html import mark_safe
from django.db.models import Count, Sum, Subquery
from django.db.models.functions import ExtractWeek, ExtractYear, ExtractMonth, TruncMonth
from django.template.response import TemplateResponse
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
# Register your models here.


@admin.register(TuyenXe)
class TuyenXeAdmin(admin.ModelAdmin):
    def has_view_or_change_permission(self, request, obj=None):
        if request.user.vai_tro_id == int(1):
            return True
        return False

    def get_urls(self):
        return [
                   path('stats/', self.stats_view)
               ] + super().get_urls()

    def stats_view(self, request):
        txe = TuyenXe.objects.annotate(sl_chuyenxe=Count('tuyen_xe'))
        datac = []
        labelsc = []
        nam = datetime.now().year
        for i in range(12):
            ds_chuyenxe = ChuyenXe.objects.filter(khoi_hanh__year=datetime.now().year,
                                              khoi_hanh__month=i+1)
            tong = 0
            for chuyenxe in ds_chuyenxe:
                tong += chuyenxe.SoLuongVeHienTai() * chuyenxe.gia_ve
            doanhthu = tong
            labelsc.append(i+1)
            datac.append(doanhthu)

        data = []
        labels = []

        for v in txe:
            labels.append(v.ten_tuyen)
            data.append(v.sl_chuyenxe)
        return TemplateResponse(request,
                                'admin/statistic.html', {
                                    'labels': labels,
                                    'data': data,
                                    'labelsc': labelsc,
                                    'datac': datac,
                                    'year': nam
                                })


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    search_fields = ['username', 'first_name']
    readonly_fields = ['hinh_anh_view']
    list_display = ['username', 'email', 'last_name', 'vai_tro']
    list_filter = ['vai_tro']

    def hinh_anh_view(self, user):
        if user:
            return mark_safe(
                '<img src="/static/{url}/" width="120" />'.format(url=user.hinh_anh.name)
            )


@admin.register(VaiTro)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ['id', 'ten_vt']
    list_display = ['id', 'ten_vt', 'so_luong']

    def so_luong(self, obj):
        rs = User.objects.filter(vai_tro_id=obj).count()
        return rs


class TaiXeFilter(SimpleListFilter):
    title = 'Tai xe'
    parameter_name = 'tai_xe'

    def lookups(self, request, model_admin):
        list_tai_xe = set([c.tai_xe for c in model_admin.model.objects.all()])
        return [(c.id, c.username) for c in list_tai_xe]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tai_xe__id=self.value())


@admin.register(ChuyenXe)
class ChuyenXeAdmin(admin.ModelAdmin):
    search_fields = ['ten_chuyenxe', 'khoi_hanh', 'tuyen_xe__diem_di', 'tuyen_xe__diem_den']
    list_display = ['ten_chuyenxe', 'khoi_hanh', 'tuyen_xe', 'tai_xe', 'sl_ghe', 'ghe_con_trong']
    list_filter = ['tuyen_xe', 'khoi_hanh', TaiXeFilter]

    def ghe_con_trong(self, obj):
        return obj.sl_ghe - obj.SoLuongVeHienTai()

    def render_change_form(self, request, context, add=True, change=False, obj=None, form_url=""):
        if request.user.vai_tro_id == int(1):
            change = True
        else:
            change = False
        context['adminform'].form.fields['tai_xe'].queryset = User.objects.filter(vai_tro_id=2)
        return super(ChuyenXeAdmin, self).render_change_form(request, context, add, change)

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(DatVe)
class DatVeAdmin(admin.ModelAdmin):
    search_fields = ['nguoi_dat', 'chuyen_xe']
    list_display = ['nguoi_dat', 'chuyen_xe', 'so_luong_ve']
    list_filter = ['chuyen_xe']

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['chuyen_xe'].queryset = ChuyenXe.objects.filter(khoi_hanh__gte=datetime.now())
        context['adminform'].form.fields['nguoi_dat'].queryset = User.objects.filter(username=request.user.username)
        return super(DatVeAdmin, self).render_change_form(request, context, *args, **kwargs)
