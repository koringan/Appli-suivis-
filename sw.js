// TrainLog v5 — Service Worker mis à jour pour GitHub Pages
const CACHE = 'trainlog-v999';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

// ─── INSTALL & ACTIVATE ───────────────────────────────────────────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => {
      return c.addAll(ASSETS).catch(err => console.warn("Erreur de mise en cache initiale:", err));
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ─── FETCH (Optimisé pour GitHub Pages) ───────────────────────────────────────
self.addEventListener('fetch', e => {
  const url = e.request.url;
  
  // Ne pas cacher les API externes
  if (url.includes('api.sncf.com') || url.includes('workers.dev') || url.includes('fonts.googleapis.com')) {
    e.respondWith(fetch(e.request).catch(() => new Response('', { status: 503 })));
    return;
  }

  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).catch(() => {
        // En cas de panne réseau complète sur index.html
        if (e.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});

// ─── PUSH NOTIFICATIONS ───────────────────────────────────────────────────────
self.addEventListener('push', e => {
  if (!e.data) return;
  let data = {};
  try { data = e.data.json(); } catch(err) { data = { title: e.data.text() }; }

  const title = data.title || 'TrainLog';
  const options = {
    body: data.body || '',
    icon: './icon-192.png',
    badge: './icon-192.png',
    data: data,
    requireInteraction: true,
    tag: `trainlog-${data.data?.trainNumber || 'notif'}`,
  };
  e.waitUntil(self.registration.showNotification(title, options));
});

// ─── CLIC SUR UNE NOTIFICATION ────────────────────────────────────────────────
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const action = e.action;
  const tchooUrl = e.notification.data?.tchooUrl;
  const appUrl = self.location.origin + self.location.pathname;

  const urlToOpen = (action === 'view-map' && tchooUrl) ? tchooUrl : appUrl;

  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if (client.url.startsWith(appUrl) && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(urlToOpen);
    })
  );
});

// ─── SUBSCRIPTION EXPIRÉE ─────────────────────────────────────────────────────
self.addEventListener('pushsubscriptionchange', e => {
  e.waitUntil(
    self.registration.pushManager.subscribe(e.oldSubscription.options)
      .then(subscription => {
        return self.clients.matchAll().then(clients => {
          clients.forEach(c => c.postMessage({ type: 'PUSH_SUBSCRIPTION_CHANGE', subscription }));
        });
      })
  );
});
