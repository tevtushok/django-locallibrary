# Generated by Django 3.0.3 on 2020-02-09 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20200208_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='due_back',
            field=models.DateField(blank=True, help_text='Book return date', null=True),
        ),
    ]