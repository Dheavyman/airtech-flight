# Generated by Django 2.1.7 on 2019-03-27 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='passport_photo',
            field=models.ImageField(upload_to='profile_pics/%Y/%m/%d/'),
        ),
    ]
