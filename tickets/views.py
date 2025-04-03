from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Ticket, TicketComment, Notification
from .forms import TicketForm, TicketStatusForm, TicketCommentForm

@login_required
def ticket_list(request):
    """
    View for listing tickets.
    """
    # For regular users, show only their tickets
    if not request.user.is_admin and not request.user.is_staff:
        tickets = Ticket.objects.filter(created_by=request.user)
    # For admins, show all tickets
    else:
        tickets = Ticket.objects.all()
        
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_create(request):
    """
    View for creating a new ticket.
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Create notification tasks for admins
            for admin in get_admin_users():
                from .task_manager import TaskManager
                TaskManager.create_task(
                    'send_notification',
                    {
                        'user_id': admin.id,
                        'ticket_id': ticket.id,
                        'message': f'Tiket baru dibuat: {ticket.title}'
                    }
                )
            
            # Send notification via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'notification_message',
                    'message': f'Tiket baru dibuat: {ticket.title}',
                    'ticket_id': ticket.id,
                }
            )
            
            # Create task to auto-assign the ticket
            from .task_manager import TaskManager
            TaskManager.create_task(
                'process_ticket',
                {
                    'ticket_id': ticket.id,
                    'action': 'auto_assign'
                }
            )
            
            messages.success(request, 'Tiket berhasil dibuat.')
            return redirect('ticket_detail', pk=ticket.id)
    else:
        form = TicketForm()
    
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Buat Tiket Baru'})

@login_required
def ticket_detail(request, pk):
    """
    View for viewing ticket details.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Check if user has permission to view this ticket
    if not request.user.is_admin and not request.user.is_staff and ticket.created_by != request.user:
        messages.error(request, 'Anda tidak memiliki izin untuk melihat tiket ini.')
        return redirect('dashboard')
    
    # Handle comment form
    if request.method == 'POST':
        # Don't allow comments on resolved tickets
        if ticket.status == 'resolved':
            messages.error(request, 'Tidak dapat menambahkan komentar pada tiket yang sudah selesai.')
            return redirect('ticket_detail', pk=ticket.id)
            
        comment_form = TicketCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            
            from .task_manager import TaskManager
            
            # Create notification for ticket owner if comment is from admin
            if request.user.is_admin or request.user.is_staff:
                if ticket.created_by != request.user:
                    # Create notification task
                    TaskManager.create_task(
                        'send_notification',
                        {
                            'user_id': ticket.created_by.id,
                            'ticket_id': ticket.id,
                            'message': f'Komentar baru pada tiket: {ticket.title}'
                        }
                    )
                    
                    # Send notification via WebSocket
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'user_{ticket.created_by.id}',
                        {
                            'type': 'notification_message',
                            'message': f'Komentar baru pada tiket: {ticket.title}',
                            'ticket_id': ticket.id,
                        }
                    )
                    
                    # Create task to send email notification
                    TaskManager.create_task(
                        'send_email',
                        {
                            'recipient': ticket.created_by.email if hasattr(ticket.created_by, 'email') else None,
                            'subject': f'Komentar Baru pada Tiket: {ticket.title}',
                            'template': 'emails/new_comment.html',
                            'context': {
                                'ticket': {
                                    'id': ticket.id,
                                    'title': ticket.title
                                },
                                'comment': {
                                    'content': comment.content,
                                    'author': request.user.username
                                }
                            }
                        }
                    )
            # Create notification for admins if comment is from user
            else:
                for admin in get_admin_users():
                    # Create notification task
                    TaskManager.create_task(
                        'send_notification',
                        {
                            'user_id': admin.id,
                            'ticket_id': ticket.id,
                            'message': f'Komentar baru pada tiket: {ticket.title}'
                        }
                    )
                
                # Send notification via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_notifications',
                    {
                        'type': 'notification_message',
                        'message': f'Komentar baru pada tiket: {ticket.title}',
                        'ticket_id': ticket.id,
                    }
                )
            
            messages.success(request, 'Komentar berhasil ditambahkan.')
            return redirect('ticket_detail', pk=ticket.id)
    else:
        # Only create comment form if ticket is not resolved
        comment_form = TicketCommentForm() if ticket.status != 'resolved' else None
    
    # Status form for admins
    status_form = None
    if request.user.is_admin or request.user.is_staff:
        status_form = TicketStatusForm(instance=ticket)
    
    # Get comments
    comments = ticket.comments.all()
    
    # Mark notifications as read
    Notification.objects.filter(user=request.user, ticket=ticket, is_read=False).update(is_read=True)
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'status_form': status_form,
    }
    
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def ticket_update_status(request, pk):
    """
    View for updating ticket status (admin only).
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Check if user has permission to update status
    if not request.user.is_admin and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk mengubah status tiket.')
        return redirect('ticket_detail', pk=ticket.id)
    
    if request.method == 'POST':
        old_status = ticket.get_status_display()
        form = TicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            new_status = ticket.get_status_display()
            
            from .task_manager import TaskManager
            
            # Create notification for ticket owner
            if ticket.created_by != request.user:
                # Create notification task
                TaskManager.create_task(
                    'send_notification',
                    {
                        'user_id': ticket.created_by.id,
                        'ticket_id': ticket.id,
                        'message': f'Status tiket berubah dari {old_status} menjadi {new_status}'
                    }
                )
                
                # Send notification via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{ticket.created_by.id}',
                    {
                        'type': 'notification_message',
                        'message': f'Status tiket berubah dari {old_status} menjadi {new_status}',
                        'ticket_id': ticket.id,
                        'refresh': True,
                    }
                )
                
                # Create task to send email notification
                TaskManager.create_task(
                    'send_email',
                    {
                        'recipient': ticket.created_by.email if hasattr(ticket.created_by, 'email') else None,
                        'subject': f'Status Tiket Diperbarui: {ticket.title}',
                        'template': 'emails/status_update.html',
                        'context': {
                            'ticket': {
                                'id': ticket.id,
                                'title': ticket.title
                            },
                            'old_status': old_status,
                            'new_status': new_status
                        }
                    }
                )
                
                # If ticket is resolved, create task to auto-close it after some time
                if new_status == 'Selesai':
                    from datetime import timedelta
                    from django.utils import timezone
                    
                    # Schedule task to run after 7 days
                    scheduled_time = timezone.now() + timedelta(days=7)
                    
                    TaskManager.create_task(
                        'process_ticket',
                        {
                            'ticket_id': ticket.id,
                            'action': 'auto_close'
                        },
                        scheduled_at=scheduled_time
                    )
            
            messages.success(request, f'Status tiket berhasil diubah menjadi {new_status}.')
            
    return redirect('ticket_detail', pk=ticket.id)

@login_required
def admin_dashboard(request):
    """
    View for admin dashboard.
    """
    # Check if user has permission to access admin dashboard
    if not request.user.is_admin and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('dashboard')
    
    # Get status filter
    status = request.GET.get('status')
    
    # Get ticket statistics
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    
    # Get tickets based on filter
    if status:
        all_tickets = Ticket.objects.filter(status=status).order_by('-created_at')
    else:
        all_tickets = Ticket.objects.all().order_by('-created_at')
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    # Get pending tasks
    from .models import Task
    pending_tasks = Task.objects.filter(status='pending').order_by('-created_at')[:10]
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'all_tickets': all_tickets,
        'unread_notifications': unread_notifications,
        'pending_tasks': pending_tasks,
        'status': status,
    }
    
    return render(request, 'tickets/admin_dashboard.html', context)

def get_admin_users():
    """
    Helper function to get all admin users.
    """
    from accounts.models import User
    return User.objects.filter(Q(is_admin=True) | Q(is_staff=True))
