from rest_framework.generics import ListAPIView
from .models import Notification
from .serializers import NotificationSerializer
from .utils import check_and_create_notifications


class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        check_and_create_notifications()
        return Notification.objects.all().order_by('-created_at')
