from datetime import datetime

from celery import shared_task
from panel_toolbox.models import Notification, History
from book.models import Book
from users.models import BookUser


@shared_task
def notify_users():
    print('notify_users)*&(#@)$*@)($')
    history = History.objects.filter(is_active=True, is_accepted=True)
    for i in history:
        if i.end_date.day - datetime.now().day <= 3:
            print(datetime.now().day - i.end_date.day)
            Notification.objects.create(
                user_id=i.user_id,
                description=f'Fuck you, {i.user.username}! You have to return {i.book.name} in '
                            f'{i.end_date.day - datetime.now().day} days!',
                type='TW',
                title='Time Warning',
                metadata={'book_id': i.book_id},
            )