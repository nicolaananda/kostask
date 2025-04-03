from django.contrib import admin
from .models import Ticket, TicketComment, Notification

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Ticket model.
    """
    list_display = ('id', 'title', 'status', 'created_by', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Informasi Tiket', {
            'fields': ('title', 'description', 'status')
        }),
        ('Informasi Pengguna', {
            'fields': ('created_by',)
        }),
        ('Informasi Waktu', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TicketComment model.
    """
    list_display = ('id', 'ticket', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'ticket__title', 'author__username')
    readonly_fields = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """
    list_display = ('id', 'user', 'ticket', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username', 'ticket__title')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
