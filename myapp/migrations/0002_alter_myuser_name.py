# Generated by Django 5.0.3 on 2024-04-03 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='name',
            field=models.CharField(blank=True, default=1, max_length=100),
            preserve_default=False,
        ),
    ]
