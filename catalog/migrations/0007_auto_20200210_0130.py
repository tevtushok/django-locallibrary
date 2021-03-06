# Generated by Django 3.0.3 on 2020-02-09 23:30

from django.db import migrations
import isbn_field.fields
import isbn_field.validators


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20200209_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=isbn_field.fields.ISBNField(clean_isbn=False, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>', max_length=28, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN'),
        ),
    ]
