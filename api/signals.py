from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from firebase_config import messaging, db
import datetime


@receiver(post_save, sender=Mander)
def update_user_mander(sender, instance, created, **kwargs):
    if created:
        related_user = instance.user_id_user
        related_user.ismander_user = True
        related_user.save()
    else:
        related_user = instance.user_id_user
        related_user.ismander_user = True
        related_user.save()

@receiver(post_delete, sender=Mander)
def delete_user_mander(sender, instance, **kwargs):
    related_user = instance.user_id_user
    related_user.ismander_user = False
    related_user.save()

@receiver(post_save, sender=Request)
def send_notification_on_request_creation(sender, instance, created, **kwargs):
    if created:
        title='NUEVO MANDADO'
        body=f'Detalle: {instance.detail_request}'
        idrequest=f'{instance.id_request}'
        topic='popayan_new_request'
        message = message_to_all_manders(title, body, topic, idrequest)
        response = messaging.send(message)
        print('Notificación enviada:', response)

def message_to_all_manders(mTitle, mBody, mTopic, mIdRequest):
    message = messaging.Message(
        data={
            'title': mTitle,
            'body': mBody,
            'idrequest': mIdRequest,
            'to': 'mander',
        },
        topic=mTopic,
    )
    return message

@receiver(post_save, sender=Requestmanager)
def update_request_status(sender, instance, created, **kwargs):
    if created:
        related_request = instance.request_id_request
        related_request.status_request = 'Proceso'
        related_request.save()
        idrequest = f'{related_request.id_request}'
        detailrequest = f'{related_request.detail_request}'
        iduser = f'{related_request.user_id_user_id}'
        idmander = f'{instance.mander_id_mander.user_id_user_id}'
        statusrequest = f'{related_request.status_request}'
        send_notification_user(idrequest, detailrequest, iduser, statusrequest, '')
        send_notification_mander(idrequest, detailrequest, idmander, statusrequest)
        
    if instance.status_requestmanager == 'terminado':
        request_instance = instance.request_id_request
        request_instance.status_request = 'Finalizado'
        request_instance.save()
        idrequest = f'{request_instance.id_request}'
        detailrequest = f'{request_instance.detail_request}'
        iduser = f'{request_instance.user_id_user_id}'
        statusrequest = f'{request_instance.status_request}'
        imagerequest = f'{instance.image_requestmanager}'
        send_notification_user(idrequest, detailrequest, iduser, statusrequest, imagerequest)

def send_notification_user(idrequest, detailrequest, iduser, statusrequest, image):
    user_id = iduser
    token = get_token(user_id)
    if token:
        title = f'Actualización --> {detailrequest}.'
        body = f'Estado: {statusrequest}.'
        message = message_to_user(title, body, token, idrequest, image)
        response = messaging.send(message)
        print('Notification sent:', response)
    else:
        print(f'No se encontró el token para el usuario con user_id: {user_id}')

def message_to_user(mTitle, mBody, mtoken, mIdRequest, mImage):
    message = messaging.Message(
        data={
            'title': mTitle,
            'body': mBody,
            'idrequest': mIdRequest,
            'image': mImage,
            'to': 'user',
        },
        token=mtoken,
    )
    return message

def send_notification_mander(idrequest, detailrequest, idmander, statusrequest):
    token = get_token(idmander)
    if token:
        title = f'Mandado Asignado.'
        body = f'Detalle: {detailrequest}, estado: {statusrequest}.'
        message = message_to_mander(title, body, token, idrequest)
        #print(message)
        response = messaging.send(message)
        print('Notification sent:', response)
    else:
        print(f'No se encontró el token para el usuario con id: {idmander}')

def message_to_mander(mTitle, mBody, mtoken, mIdRequest):
    message = messaging.Message(
        data={
            'title': mTitle,
            'body': mBody,
            'idrequest': mIdRequest,
            'to': 'mander',
        },
        token=mtoken,
    )
    return message

def get_token(id):
    try:
        ref = db.reference(f'Manders/Tokens/{id}/token')
        token = ref.get()
        print(token)
        return token
    except Exception as e:
        print(f"Error al consultar la base de datos Firebase: {e}")
        return None

@receiver(post_save, sender=Vehicle)
def update_user_vehicles(sender, instance, created, **kwargs):
    if instance.isactive_vehicle:
        user_vehicles = Vehicle.objects.filter(user_id_user=instance.user_id_user)
        user_vehicles.exclude(id_vehicle=instance.id_vehicle).update(isactive_vehicle=False)