// WebSocket connection for real-time notifications
document.addEventListener('DOMContentLoaded', function() {
    // Create WebSocket connection
    const host = window.location.hostname;
    const ticketSocket = new WebSocket(
        'ws://' + host + ':8001/ws/notifications/'
    );

    ticketSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        showNotification(data.message);
        
        // Refresh the page to show updated ticket status
        if (data.refresh) {
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }
        
        // Dispatch a custom event for ticket-specific pages
        window.dispatchEvent(new MessageEvent('message', {
            data: {
                type: 'websocket_message',
                payload: data
            }
        }));
    };

    ticketSocket.onclose = function(e) {
        console.error('Ticket socket closed unexpectedly');
    };

    // Function to show notification
    function showNotification(message) {
        const notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) return;
        
        const notification = document.createElement('div');
        notification.className = 'toast show';
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');
        
        notification.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">KostTicket</strong>
                <small>Baru saja</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        notificationContainer.appendChild(notification);
        
        // Auto-remove notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
});
