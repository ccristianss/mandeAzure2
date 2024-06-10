from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from firebase_config import messaging, db
import datetime


@receiver(post_save, sender=Mander)
def update_user_mander(sender, instance, created, **kwargs):
    related_user = instance.user_id_user
    if created or not related_user.ismander_user:
        related_user.ismander_user = True
        related_user.save()

@receiver(post_delete, sender=Mander)
def delete_user_mander(sender, instance, **kwargs):
    related_user = instance.user_id_user
    if related_user.ismander_user:
        related_user.ismander_user = False
        related_user.save()

@receiver(post_save, sender=Request)
def send_notification_on_request_creation(sender, instance, created, **kwargs):
    if created:
        title='NUEVO MANDADO'
        body=f'Detalle: {instance.detail_request}'
        idrequest=str(instance.id_request)
        ispriority=str(instance.ispriority_request)
        typevehicle=str(instance.typevehicle_request)
        topic='popayan_new_request'
        
        # Notification to all manders
        message = messaging.Message(
            data={
                'title': title,
                'body': body,
                'idrequest': idrequest,
                'to': 'mander',
            },
            topic=topic,
        )
        try:
            response = messaging.send(message)
            print('Notificación enviada:', response)
        except messaging.UnregisteredError:
            print('Token no registrado para mander. Eliminando token...')

        # Notification to admin
        admin_token = get_token('admin')
        if admin_token:
            admin_message = messaging.Message(
                data={
                    'title': title,
                    'body': body,
                    'idrequest': idrequest,
                    'ispriority': ispriority,
                    'typevehicle': typevehicle,
                    'to': 'admin',
                },
                token=admin_token,
            )
            try:
                admin_response = messaging.send(admin_message)
                print('Notificación enviada a admin:', admin_response)
            except messaging.UnregisteredError:
                print('Token no registrado para admin. Eliminando token...')
        else:
            print('No se encontró el token para admin')

@receiver(post_save, sender=Requestmanager)
def update_request_status(sender, instance, created, **kwargs):
    related_request = instance.request_id_request
    if created:
        related_request.status_request = 'Proceso'
        related_request.save()
        notify_users_and_manders(related_request, instance.mander_id_mander.user_id_user_id, 'Proceso', '')
        
    elif instance.status_requestmanager == 'terminado':
        related_request.status_request = 'Finalizado'
        related_request.save()
        notify_users_and_manders(related_request, None, 'Finalizado', instance.image_requestmanager)

def notify_users_and_manders(request_instance, mander_user_id, status, image):
    idrequest = str(request_instance.id_request)
    detailrequest = str(request_instance.detail_request)
    iduser = str(request_instance.user_id_user_id)
    
    send_notification_user(idrequest, detailrequest, iduser, status, image)
    if mander_user_id:
        send_notification_mander(idrequest, detailrequest, mander_user_id, status)

def send_notification_user(idrequest, detailrequest, iduser, statusrequest, image):
    token = get_token(iduser)
    if token:
        title = f'Actualización --> {detailrequest}.'
        body = f'Estado: {statusrequest}.'
        message = messaging.Message(
            data={
                'title': title,
                'body': body,
                'idrequest': idrequest,
                'image': str(image),
                'to': 'user',
            },
            token=token,
        )
        try:
            response = messaging.send(message)
            print('Notification sent:', response)
        except messaging.UnregisteredError:
            print(f'Token no registrado para el usuario con user_id: {iduser}. Eliminando token...')
            delete_token(iduser)
    else:
        print(f'No se encontró el token para el usuario con user_id: {iduser}')

def send_notification_mander(idrequest, detailrequest, idmander, statusrequest):
    token = get_token(idmander)
    if token:
        title = f'Mandado Asignado.'
        body = f'Detalle: {detailrequest}, estado: {statusrequest}.'
        message = messaging.Message(
            data={
                'title': title,
                'body': body,
                'idrequest': idrequest,
                'to': 'mander',
            },
            token=token,
        )
        try:
            response = messaging.send(message)
            print('Notification sent:', response)
        except messaging.UnregisteredError:
            print(f'Token no registrado para el mander con user_id: {idmander}. Eliminando token...')
            delete_token(idmander)
    else:
        print(f'No se encontró el token para el usuario con id: {idmander}')

def get_token(id):
    try:
        ref = db.reference(f'Manders/Tokens/{id}/token')
        token = ref.get()
        print(token)
        return token
    except Exception as e:
        print(f"Error al consultar la base de datos Firebase: {e}")
        return None

def delete_token(id):
    try:
        ref = db.reference(f'Manders/Tokens/{id}')
        ref.delete()
        print(f'Token eliminado para el id: {id}')
    except Exception as e:
        print(f"Error al eliminar el token en Firebase: {e}")
        
@receiver(post_save, sender=Vehicle)
def update_user_vehicles(sender, instance, created, **kwargs):
    if instance.isactive_vehicle:
        Vehicle.objects.filter(user_id_user=instance.user_id_user).exclude(id_vehicle=instance.id_vehicle).update(isactive_vehicle=False)