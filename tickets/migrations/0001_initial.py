# Generated by Django 5.2 on 2025-04-03 04:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Judul')),
                ('description', models.TextField(verbose_name='Deskripsi')),
                ('status', models.CharField(choices=[('open', 'Terbuka'), ('in_progress', 'Sedang Diproses'), ('resolved', 'Selesai')], default='open', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Tanggal dibuat')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Terakhir diperbarui')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL, verbose_name='Dibuat oleh')),
            ],
            options={
                'verbose_name': 'Tiket',
                'verbose_name_plural': 'Tiket',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255, verbose_name='Pesan')),
                ('is_read', models.BooleanField(default=False, verbose_name='Sudah dibaca')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Tanggal dibuat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Pengguna')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='tickets.ticket', verbose_name='Tiket')),
            ],
            options={
                'verbose_name': 'Notifikasi',
                'verbose_name_plural': 'Notifikasi',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Konten')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Tanggal dibuat')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_comments', to=settings.AUTH_USER_MODEL, verbose_name='Penulis')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket', verbose_name='Tiket')),
            ],
            options={
                'verbose_name': 'Komentar Tiket',
                'verbose_name_plural': 'Komentar Tiket',
                'ordering': ['created_at'],
            },
        ),
    ]
