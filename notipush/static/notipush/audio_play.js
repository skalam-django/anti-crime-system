$(document).ready(function(){
channel.addEventListener('message', event => {
  console.log('Received', event.data);
  // play_audio(event.data.audio_url);
  say(event.data.narrative);
});

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
});


