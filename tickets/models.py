from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    """
    Model for ticket reporting.
    """
    STATUS_CHOICES = (
        ('open', _('Terbuka')),
        ('in_progress', _('Sedang Diproses')),
        ('resolved', _('Selesai')),
    )
    
    title = models.CharField(_('Judul'), max_length=100)
    description = models.TextField(_('Deskripsi'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('Dibuat oleh')
    )
    created_at = models.DateTimeField(_('Tanggal dibuat'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Terakhir diperbarui'), auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Tiket')
        verbose_name_plural = _('Tiket')
    
    def __str__(self):
        return self.title

class TicketComment(models.Model):
    """
    Model for comments on tickets.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Tiket')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_comments',
        verbose_name=_('Penulis')
    )
    content = models.TextField(_('Konten'))
    created_at = models.DateTimeField(_('Tanggal dibuat'), auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Komentar Tiket')
        verbose_name_plural = _('Komentar Tiket')
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.ticket.title}'

class Notification(models.Model):
    """
    Model for storing notifications.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Pengguna')
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Tiket')
    )
    message = models.CharField(_('Pesan'), max_length=255)
    is_read = models.BooleanField(_('Sudah dibaca'), default=False)
    created_at = models.DateTimeField(_('Tanggal dibuat'), auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notifikasi')
        verbose_name_plural = _('Notifikasi')
    
    def __str__(self):
        return self.message

class Task(models.Model):
    """
    Model for task queue.
    """
    TASK_TYPES = (
        ('send_notification', _('Kirim Notifikasi')),
        ('generate_report', _('Buat Laporan')),
        ('send_email', _('Kirim Email')),
        ('process_ticket', _('Proses Tiket')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Menunggu')),
        ('processing', _('Sedang Diproses')),
        ('completed', _('Selesai')),
        ('failed', _('Gagal')),
    )
    
    task_type = models.CharField(_('Jenis Tugas'), max_length=50, choices=TASK_TYPES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    data = models.JSONField(_('Data'), default=dict, blank=True)
    result = models.TextField(_('Hasil'), blank=True, null=True)
    error = models.TextField(_('Error'), blank=True, null=True)
    created_at = models.DateTimeField(_('Tanggal dibuat'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Terakhir diperbarui'), auto_now=True)
    scheduled_at = models.DateTimeField(_('Dijadwalkan pada'), null=True, blank=True)
    executed_at = models.DateTimeField(_('Dieksekusi pada'), null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Tugas')
        verbose_name_plural = _('Tugas')
    
    def __str__(self):
        return f"{self.task_type} - {self.status} ({self.created_at})"
