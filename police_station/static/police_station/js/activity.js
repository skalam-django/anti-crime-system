$( document ).ready(function(){
	if (!window.Promise) {
	  window.Promise = Promise;
	}

	if ('serviceWorker' in navigator) {
	  navigator.serviceWorker
	    .register('/activity_sw.js')
	    .then(function () {
	      console.log('Service worker registered!');
	    })
	    .catch(function(err) {
	      console.log(err);
	    });
	}

	window.addEventListener('beforeinstallprompt', function(event) {
	  console.log('beforeinstallprompt fired');
	  event.preventDefault();
	  deferredPrompt = event;
	  return false;
	});

	function displayConfirmNotification() {
	  if ('serviceWorker' in navigator) {
	    var options = {
	      body: 'You successfully subscribed to our Notification service!',
	      icon: '/static/police_station/images/icons/app-icon-96x96.png',
	      // image: '/static/images/sf-boat.jpg',
	      dir: 'ltr',
	      lang: 'en-US', // BCP 47,
	      vibrate: [100, 50, 200],
	      badge: '/static/police_station/images/icons/app-icon-96x96.png',
	      tag: 'confirm-notification',
	      renotify: true,
	      actions: [
	        { action: 'confirm', title: 'Okay', icon: '/static/police_station/images/icons/app-icon-96x96.png' },
	        { action: 'cancel', title: 'Cancel', icon: '/static/police_station/images/icons/app-icon-96x96.png' }
	      ]
	    };

	    navigator.serviceWorker.ready
	      .then(function(swreg) {
	        swreg.showNotification('Successfully subscribed!', options);
	      });
	  }
	}

	function configurePushSub() {
	  if (!('serviceWorker' in navigator)) {
	    return;
	  }

	  var reg;
	  navigator.serviceWorker.ready
	    .then(function(swreg) {
	      reg = swreg;
	      return swreg.pushManager.getSubscription();
	    })
	    .then(function(sub) {
	    	console.log('sub: ',sub);
	      if (sub === null) {
	        // Create a new subscription
	        var vapidPublicKey = 'BDPXgINzfT7Lbb-FIaiMAVD-tsB3cix5K4osVk5MCAn8hVpt8S-tfMGBUXKx4gpArUrwpdVHYoJavF7za4uMW34';
	        var convertedVapidPublicKey = urlBase64ToUint8Array(vapidPublicKey);
	        return reg.pushManager.subscribe({
	          userVisibleOnly: true,
	          applicationServerKey: convertedVapidPublicKey
	        });
	      } else {
	        // We have a subscription
	      }
	    })
	    .then(function(newSub) {
	    	// return true;
	    	console.log(newSub,'newSub');
	      return fetch('https://e73efbe8.ngrok.io/police_station/subscriptions', {
	        method: 'POST',
	        headers: {
	          'Content-Type': 'application/json',
	          'Accept': 'application/json'
	        },
	        body: JSON.stringify(newSub)
	      })
	    })
	    .then(function(res) {
	      if (res.ok) {
	      	// if (res==true){
	        // displayConfirmNotification();
	      }
	    })
	    .catch(function(err) {
	      console.log(err);
	    });
	}

	function askForNotificationPermission() {
	  Notification.requestPermission(function(result) {
	    console.log('User Choice', result);
	    if (result !== 'granted') {
	      console.log('No notification permission granted!');
	    } else {
	      configurePushSub();
	      // displayConfirmNotification();
	    }
	  });
	}

	if ('Notification' in window && 'serviceWorker' in navigator) {
		askForNotificationPermission();
	}
	// set_default_marker_position();

});

