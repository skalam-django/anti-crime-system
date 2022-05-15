// self.importScripts('/static/notipush/audio_play.js');

// const channel = new BroadcastChannel('sw-messages');

var channel = new BroadcastChannel('sw-messages');
// importScripts('/static/notipush/notipush.js');
var CACHE_STATIC_NAME = 'static-v27';
var CACHE_DYNAMIC_NAME = 'dynamic-v5';
var STATIC_FILES = [
  '/static/notipush/notipush.js',
  // '/static/notipush/audio_play.js',
];

self.addEventListener('install', function (event) {
  // console.log('[Service Worker] Installing Service Worker ...', event);
  event.waitUntil(
    caches.open(CACHE_STATIC_NAME)
      .then(function (cache) {
        // console.log('[Service Worker] Precaching App Shell');
        cache.addAll(STATIC_FILES);
      })
  )
});

self.addEventListener('activate', function (event) {
  // console.log('[Service Worker] Activating Service Worker ....', event);
  event.waitUntil(
    caches.keys()
      .then(function (keyList) {
        return Promise.all(keyList.map(function (key) {
          if (key !== CACHE_STATIC_NAME && key !== CACHE_DYNAMIC_NAME) {
            // console.log('[Service Worker] Removing old cache.', key);
            return caches.delete(key);
          }
        }));
      })
  );
  return self.clients.claim();
});

self.addEventListener('push', function(event) {
  let payload =   event.data ? event.data.text() : {"head": "No Content", "body": "No Content", "icon": ""};
  var payload1=   JSON.parse(payload);
  // console.log('payload1: ',payload1);
  var event_id=   payload1.event_id;
  var data    =   payload1.data;
  
  var head    =   payload1.head;
  var body    =   payload1.body;
  var url     =   payload1.url ? payload1.url: self.location.origin;
  var vibrate =   payload1.vibrate;
  var tag     =   payload1.tag;
  var icon    =   'https://'+self.location.hostname+payload1.icon;
  // channel.postMessage({audio_url: audio_url}); 
  // say(payload1.data.narrative);
  channel.postMessage({narrative: payload1.data.narrative});         //Channel OFF
  event.waitUntil(
    self.registration.showNotification(head, {
      body: body,
      icon: icon,
      data: {url: 'https://'+self.location.hostname+url},
      vibrate: vibrate,
      icon:icon,
      tag:tag,
    })
  );
});


self.addEventListener('notificationclick', function(event) {
  var notification = event.notification;
  var action = event.action;

  console.log(notification);

  if (action === 'confirm') {
    console.log('Confirm was chosen');
    notification.close();
  } else {
    console.log(action);
    event.waitUntil(
      clients.matchAll()
        .then(function(clis) {
          var client = clis.find(function(c) {
            return c.visibilityState === 'visible';
          });

          if (client !== undefined) {
            client.navigate(notification.data.url);
            client.focus();
          } else {
            clients.openWindow(notification.data.url);
          }
          notification.close();
        })
    );
  }
});

self.addEventListener('notificationclose', function(event) {
  console.log('Notification was closed', event);
});


function playByteArray( bytes ) {
    var buffer = new Uint8Array( bytes.length );
    buffer.set( new Uint8Array(bytes), 0 );

    context.decodeAudioData(buffer.buffer, play);
}

function play( audioBuffer ) {
    var source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.connect( context.destination );
    source.start(0);
}