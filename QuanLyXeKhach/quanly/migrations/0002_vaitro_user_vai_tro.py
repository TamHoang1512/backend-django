# Generated by Django 4.0.4 on 2022-05-11 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quanly', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VaiTro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_vt', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='vai_tro',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='quanly.vaitro'),
            preserve_default=False,
        ),
    ]