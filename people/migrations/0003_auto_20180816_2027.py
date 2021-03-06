# Generated by Django 2.1 on 2018-08-16 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_auto_20180807_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverified',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AlterField(
            model_name='findpwd',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AlterField(
            model_name='follower',
            name='user_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_a', to=settings.AUTH_USER_MODEL, verbose_name='偶像'),
        ),
        migrations.AlterField(
            model_name='follower',
            name='user_b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_b', to=settings.AUTH_USER_MODEL, verbose_name='粉丝'),
        ),
    ]
