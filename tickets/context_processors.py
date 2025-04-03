from .models import Notification

def notifications_processor(request):
    """
    Context processor to add unread notifications count to all templates.
    """
    context = {
        'unread_notifications_count': 0
    }
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'is_admin') and (request.user.is_admin or request.user.is_staff):
            context['unread_notifications_count'] = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
    
    return context
