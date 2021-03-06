# Generated by Django 3.2.7 on 2021-11-14 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('personal', '0002_person_telegram_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personal.person')),
            ],
        ),
    ]
