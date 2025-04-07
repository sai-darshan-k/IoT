self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/plant3.webp', // Add an icon if you have one
      vibrate: [200, 100, 200],
      data: { url: 'https://iot-delta-vert.vercel.app/' }
    };
  
    event.waitUntil(
      self.registration.showNotification('CropCare AI', options)
    );
  });
  
  self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  });