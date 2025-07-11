# Generated by Django 5.0.2 on 2024-04-17 18:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id_account', models.AutoField(primary_key=True, serialize=False)),
                ('email_account', models.CharField(max_length=45, unique=True)),
                ('password_account', models.CharField(max_length=255)),
                ('dateregister_account', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_account', models.DateTimeField(auto_now=True)),
                ('isadmin_account', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'account',
            },
        ),
        migrations.CreateModel(
            name='Mander',
            fields=[
                ('id_mander', models.AutoField(primary_key=True, serialize=False)),
                ('image_mander', models.ImageField(blank=True, null=True, upload_to='imgMander')),
                ('ishavecar_mander', models.BooleanField()),
                ('ishavemoto_mander', models.BooleanField()),
                ('isactive_mander', models.BooleanField()),
                ('isvalidate_mander', models.BooleanField(default=False)),
                ('dateregister_mander', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_mander', models.DateTimeField(auto_now=True)),
                ('address_mander', models.CharField(max_length=100)),
                ('cc_mander', models.CharField(max_length=13, unique=True)),
            ],
            options={
                'db_table': 'mander',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id_request', models.AutoField(primary_key=True, serialize=False)),
                ('detail_request', models.CharField(max_length=255)),
                ('status_request', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Proceso', 'Proceso'), ('Finalizado', 'Finalizado')], default='Pendiente', max_length=20)),
                ('dateregister_request', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_request', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'request',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id_service', models.AutoField(primary_key=True, serialize=False)),
                ('name_service', models.CharField(max_length=45)),
                ('detail_service', models.CharField(max_length=255)),
                ('image_service', models.ImageField(blank=True, null=True, upload_to='imgService')),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='Requestmanager',
            fields=[
                ('id_requestmanager', models.AutoField(primary_key=True, serialize=False)),
                ('image_requestmanager', models.ImageField(blank=True, null=True, upload_to='imgRequestmanager')),
                ('status_requestmanager', models.CharField(choices=[('espera', 'En espera'), ('proceso', 'En proceso'), ('terminado', 'Terminado')], max_length=10)),
                ('detail_requestmanager', models.CharField(max_length=45)),
                ('dateregister_requestmanager', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_requestmanager', models.DateTimeField(auto_now=True)),
                ('mander_id_mander', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.mander')),
                ('request_id_request', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='api.request')),
            ],
            options={
                'db_table': 'requestmanager',
            },
        ),
        migrations.AddField(
            model_name='request',
            name='service_id_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.service'),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id_user', models.AutoField(primary_key=True, serialize=False)),
                ('image_user', models.ImageField(blank=True, null=True, upload_to='imgProfiles')),
                ('name_user', models.CharField(max_length=45)),
                ('lastname_user', models.CharField(max_length=45)),
                ('phone_user', models.CharField(max_length=10)),
                ('dateregister_user', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_user', models.DateTimeField(auto_now=True)),
                ('ismander_user', models.BooleanField(default=False)),
                ('account_id_account', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='api.account')),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.AddField(
            model_name='request',
            name='user_id_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.user'),
        ),
        migrations.AddField(
            model_name='mander',
            name='user_id_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='api.user'),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id_document', models.AutoField(primary_key=True, serialize=False)),
                ('image_document', models.ImageField(blank=True, null=True, upload_to='imgDocs')),
                ('isdocument_vehicle', models.BooleanField()),
                ('isverified_document', models.BooleanField(default=False)),
                ('type_document', models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('SOAT', 'SOAT'), ('LICENCIA', 'Licencia'), ('OPERACION', 'Operación'), ('TECNOMECANICA', 'Tecnomecánica'), ('RECIBO', 'Recibo')], max_length=15)),
                ('dateregister_document', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_document', models.DateTimeField(auto_now=True)),
                ('dateverified_document', models.DateTimeField(null=True)),
                ('user_id_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.user')),
            ],
            options={
                'db_table': 'document',
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id_vehicle', models.AutoField(primary_key=True, serialize=False)),
                ('image_vehicle', models.ImageField(blank=True, null=True, upload_to='imgVehicles')),
                ('brand_vehicle', models.CharField(max_length=20)),
                ('plate_vehicle', models.CharField(max_length=10, unique=True)),
                ('model_vehicle', models.CharField(max_length=4)),
                ('color_vehicle', models.CharField(max_length=45)),
                ('type_vehicle', models.CharField(choices=[('none', 'None'), ('bicycle', 'Bicycle'), ('bike', 'Motorcycle'), ('car', 'Car')], max_length=10)),
                ('isverified_vehicle', models.BooleanField(default=False)),
                ('dateregister_vehicle', models.DateTimeField(auto_now_add=True)),
                ('dateupdate_vehicle', models.DateTimeField(auto_now=True)),
                ('dateverified_vehicle', models.DateTimeField(auto_now=True)),
                ('user_id_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.user')),
            ],
            options={
                'db_table': 'vehicle',
            },
        ),
    ]
