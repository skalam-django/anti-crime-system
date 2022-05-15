var isPushEnabled = false,
  subBtn,
  messageBox,
  registration;
var channel = new BroadcastChannel('sw-messages');

$(document).ready(function() {
  subBtn = document.getElementById('notipush-subscribe-button');
  messageBox = document.getElementById('notipush-message');
  if ('serviceWorker' in navigator) { 
    var serviceWorker = document.querySelector('meta[name="service-worker-js"]').content;
    navigator.serviceWorker.register(serviceWorker)
      .then(
        function(reg) {
          registration = reg;
          
          initialiseState(registration);
        })
    }
  else {  
    messageBox.textContent = 'Service Worker is not supported in your Browser!';
    messageBox.style.display = 'block'; 
  }
  
  
  // try{
  //   subBtn.addEventListener('click',
  //     function() {
  //       subBtn.disabled = true;
  //       if (isPushEnabled) {
  //         return unsubscribe()
  //       }
  //       if ('serviceWorker' in navigator) { 
  //           subBtn.textContent = 'Loading....';
  //           // initialiseState(registration);

  //       }
  //     }
  //   );
  // }catch(e){
    
  // }

    function initialiseState(reg) {
      try{
        if (!(reg.showNotification)) {
            messageBox.textContent = 'Showing Notification is not suppoted in your browser';
            subBtn.textContent = 'Subscribe to Push Messaging';
            messageBox.style.display = 'block';
            return;
        }

        if (Notification.permission === 'denied') {
          messageBox.textContent = 'The Push Notification is blocked from your browser.';
          subBtn.textContent = 'Subscribe to Push Messaging';
          subBtn.disabled = false;
          messageBox.style.display = 'block';
          return;  
        }
        if (!('PushManager' in window)) {
          messageBox.textContent = 'Push Notification is not available in the browser';
          subBtn.textContent = 'Subscribe to Push Messaging';
          subBtn.disabled = false;
          messageBox.style.display = 'block';
          return;  
        }
        subscribe(reg);
      }catch(e){
        
      }
    }
  try{
    channel.addEventListener('message', event => {
      console.log('Received', event.data);
      // play_audio(event.data.audio_url);
      say(event.data.narrative);
    });
  }catch(e){
    
  }

   function say(m) {
    var msg = new SpeechSynthesisUtterance();
    var voices = window.speechSynthesis.getVoices();
    msg.voice = voices[10];
    msg.voiceURI = "native";
    msg.volume = 1;
    msg.rate = 1;
    msg.pitch = 0.8;
    msg.text = m;
    msg.lang = 'en-US';
    speechSynthesis.speak(msg);
  }   

  function play_audio(audio_url){
    audio = new Audio(audio_url)
    audio.play();
  }
}
);


function subscribe(reg) {
  getSubscription(reg).then(
      function(subscription) {
        postSubscribeObj('subscribe',subscription);
      }
    )
    .catch(
      function(error) {
        console.log('Subscription error.', error)
      }
    )
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function getSubscription(reg) {
    return reg.pushManager.getSubscription().then(
        function(subscription) {
          var metaObj, applicationServerKey, options;
          if (subscription) {
            return subscription;
          }

          metaObj = document.querySelector('meta[name="django-notipush-vapid-key"]');
          applicationServerKey = metaObj.content;
          options = {
              userVisibleOnly: true
          };
          if (applicationServerKey){
              options.applicationServerKey = urlB64ToUint8Array(applicationServerKey)
          }
          return registration.pushManager.subscribe(options)
        }
      )
}

function unsubscribe() {
  registration.pushManager.getSubscription()
    .then(
      function(subscription) {
        if (!subscription) {
          subBtn.disabled = false;
          messageBox.textContent = 'Subscription is not available';
          messageBox.style.display = 'block';
          return;
        }
        // postSubscribeObj('unsubscribe', subscription);
      }
    )  
}

function postSubscribeObj(statusType, subscription) {
  var browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase(),
    data = {  status_type: statusType,
              subscription: subscription.toJSON(),
              browser: browser,
              group: JSON.parse(subBtn.dataset.group.replace(/'/g, '"')),
           };       
  fetch(subBtn.dataset.url, {
    method: 'post',
    headers:  {
                'Content-Type': 'application/json',
                'X-CSRFToken' : $('input[name=csrfmiddlewaretoken]').val(),
              },
    body: JSON.stringify(data),
    credentials: 'include'
  })
    .then(
      function(response) {
        if ((response.status == 201) && (statusType == 'subscribe')) {
          // subBtn.textContent = 'Unsubscribe to Push Messaging';
          subBtn.style.display = "none";
          subBtn.disabled = true;
          isPushEnabled = true;
        }
        if ((response.status == 202) && (statusType == 'unsubscribe')) {
          getSubscription(registration)
            .then(
              function(subscription) {
                subscription.unsubscribe()
                .then(
                  function(successful) {
                    subBtn.textContent = 'Subscribe to Push Messaging';
                    isPushEnabled = false;
                    subBtn.disabled = false;
                  }
                )
              }
            )
            .catch(
              function(error) {
                subBtn.textContent = 'Unsubscribe to Push Messaging';
                messageBox.textContent = 'Error during unsubscribe from Push Notification';
                messageBox.style.display = 'block';
                subBtn.disabled = false;
              }
            );
        }
      }
    )
}





