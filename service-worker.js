// This file should be placed in your static folder or root directory
self.addEventListener('push', function(event) {
    if (event.data) {
        const notification = event.data.json();
        
        const options = {
            body: notification.body,
            icon: notification.icon || '/static/icon.png', // Default icon
            badge: notification.badge || '/static/badge.png', // Default badge
            tag: notification.tag || 'cropcare-notification',
            renotify: notification.renotify || false,
            data: {
                url: self.registration.scope // URL to open when notification is clicked
            }
        };
        
        event.waitUntil(
            self.registration.showNotification(notification.title || 'CropCare AI Alert', options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    // This looks to see if the current is already open and focuses if it is
    event.waitUntil(
        clients.matchAll({
            type: "window"
        })
        .then(function(clientList) {
            for (var i = 0; i < clientList.length; i++) {
                var client = clientList[i];
                if (client.url === '/' && 'focus' in client)
                    return client.focus();
            }
            if (clients.openWindow)
                return clients.openWindow('/');
        })
    );
});