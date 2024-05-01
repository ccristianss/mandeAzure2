from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Requestmanager, Request, Mander, User
from firebase_config import messaging, db


@receiver(post_save, sender=Requestmanager)
def update_request_status(sender, instance, created, **kwargs):
    if created:
        # Obtener el objeto Request asociado al Requestmanager
        related_request = instance.request_id_request

        # Actualizar el status_request a 'Proceso'
        related_request.status_request = 'Proceso'
        related_request.save()
        
    if instance.status_requestmanager == 'terminado':
        # Obtener el objeto Request relacionado
        request_instance = instance.request_id_request
        # Actualizar el campo status_request a 'Finalizado'
        request_instance.status_request = 'Finalizado'
        request_instance.save()

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
        # Crea el mensaje de notificación
        message = messaging.Message(
            notification=messaging.Notification(
                title='Nuevo pedido creado',
                body=f'Se ha creado un nuevo pedido: {instance.detail_request}'
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    priority='high',
                ),
            ),
            topic='new_request_popayan',   # Puedes enviar la notificación a un tema específico
        )

        response = messaging.send(message)
        print('Notificación enviada:', response)

@receiver(post_save, sender=Request)
def send_notification_on_request_update(sender, instance, **kwargs):
    user_id = instance.user_id_user_id
    print(user_id)
    ref = db.reference(f'Manders/Tokens/{user_id}/token')
    token = ref.get()

    if token:
        message = messaging.Message(
            notification=messaging.Notification(
                title='Actualización de solicitud',
                body=f'Se ha actualizado la solicitud {instance.detail_request}',
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    priority='high',
                ),
            ),
            token=token,
        )
        response = messaging.send(message)
        print('Notification sent:', response)
    else:
        print(f'No se encontró el token para el usuario con user_id: {user_id}')