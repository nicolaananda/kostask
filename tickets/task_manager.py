import json
import logging
import traceback
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from .models import Task, Notification, Ticket
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manager for handling task queue operations.
    """
    
    @staticmethod
    def create_task(task_type, data=None, scheduled_at=None):
        """
        Create a new task in the queue.
        
        Args:
            task_type (str): Type of task to create
            data (dict): Data needed for the task
            scheduled_at (datetime): When to execute the task
            
        Returns:
            Task: The created task
        """
        if data is None:
            data = {}
            
        task = Task.objects.create(
            task_type=task_type,
            data=data,
            scheduled_at=scheduled_at
        )
        logger.info(f"Task created: {task.id} - {task.task_type}")
        return task
    
    @staticmethod
    def process_next_task():
        """
        Process the next pending task in the queue.
        
        Returns:
            bool: True if a task was processed, False otherwise
        """
        # Get the next pending task
        next_task = Task.objects.filter(
            status='pending'
        ).filter(
            Q(scheduled_at__lte=timezone.now()) | Q(scheduled_at__isnull=True)
        ).order_by('created_at').first()
        
        if not next_task:
            return False
            
        # Mark task as processing
        next_task.status = 'processing'
        next_task.save()
        
        try:
            # Execute the task based on its type
            if next_task.task_type == 'send_notification':
                TaskManager._process_send_notification(next_task)
            elif next_task.task_type == 'generate_report':
                TaskManager._process_generate_report(next_task)
            elif next_task.task_type == 'send_email':
                TaskManager._process_send_email(next_task)
            elif next_task.task_type == 'process_ticket':
                TaskManager._process_ticket(next_task)
            else:
                raise ValueError(f"Unknown task type: {next_task.task_type}")
                
            # Mark task as completed
            next_task.status = 'completed'
            next_task.executed_at = timezone.now()
            next_task.save()
            logger.info(f"Task completed: {next_task.id} - {next_task.task_type}")
            return True
            
        except Exception as e:
            # Mark task as failed
            next_task.status = 'failed'
            next_task.error = traceback.format_exc()
            next_task.save()
            logger.error(f"Task failed: {next_task.id} - {next_task.task_type}: {str(e)}")
            return False
    
    @staticmethod
    def _process_send_notification(task):
        """Process a send_notification task."""
        data = task.data
        user_id = data.get('user_id')
        ticket_id = data.get('ticket_id')
        message = data.get('message')
        
        if not all([user_id, ticket_id, message]):
            raise ValueError("Missing required data for send_notification task")
            
        from accounts.models import User
        user = User.objects.get(id=user_id)
        ticket = Ticket.objects.get(id=ticket_id)
        
        notification = Notification.objects.create(
            user=user,
            ticket=ticket,
            message=message
        )
        
        task.result = f"Notification created: {notification.id}"
        return notification
    
    @staticmethod
    def _process_generate_report(task):
        """Process a generate_report task."""
        data = task.data
        report_type = data.get('report_type')
        
        if report_type == 'ticket_summary':
            # Generate ticket summary report
            open_count = Ticket.objects.filter(status='open').count()
            in_progress_count = Ticket.objects.filter(status='in_progress').count()
            resolved_count = Ticket.objects.filter(status='resolved').count()
            total_count = Ticket.objects.count()
            
            report = {
                'open_count': open_count,
                'in_progress_count': in_progress_count,
                'resolved_count': resolved_count,
                'total_count': total_count,
                'generated_at': timezone.now().isoformat()
            }
            
            task.result = json.dumps(report)
            return report
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    @staticmethod
    def _process_send_email(task):
        """Process a send_email task."""
        data = task.data
        recipient = data.get('recipient')
        subject = data.get('subject')
        template = data.get('template')
        context = data.get('context', {})
        
        if not all([recipient, subject, template]):
            raise ValueError("Missing required data for send_email task")
            
        # Render email content from template
        html_content = render_to_string(template, context)
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Plain text version (empty)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_content,
            fail_silently=False
        )
        
        task.result = f"Email sent to {recipient}"
        return True
    
    @staticmethod
    def _process_ticket(task):
        """Process a process_ticket task."""
        data = task.data
        ticket_id = data.get('ticket_id')
        action = data.get('action')
        
        if not all([ticket_id, action]):
            raise ValueError("Missing required data for process_ticket task")
            
        ticket = Ticket.objects.get(id=ticket_id)
        
        if action == 'auto_assign':
            # Auto-assign ticket to an admin
            from accounts.models import User
            admin = User.objects.filter(Q(is_admin=True) | Q(is_staff=True)).first()
            
            if admin:
                # In a real implementation, you would update the ticket with the assigned admin
                # For now, we'll just log it
                task.result = f"Ticket {ticket_id} auto-assigned to {admin.username}"
            else:
                task.result = f"No admin available to assign ticket {ticket_id}"
                
        elif action == 'auto_close':
            # Auto-close tickets that have been in progress for too long
            if ticket.status == 'in_progress':
                ticket.status = 'resolved'
                ticket.save()
                task.result = f"Ticket {ticket_id} auto-closed"
            else:
                task.result = f"Ticket {ticket_id} not closed (status: {ticket.status})"
        else:
            raise ValueError(f"Unknown ticket action: {action}")
            
        return True
