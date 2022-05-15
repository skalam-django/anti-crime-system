let scanner;
$( document ).ready(function(){
  var videoSelect = document.querySelector('select#videoSource');
  scanner= new Instascan.Scanner(
              {
                  video: document.getElementById('video')
              }
          );
    scanner.addListener('scan', function(url) {
      stop_scan();
      $('#loader').css('display','block');
      if(url!=undefined){
        var smart_ajax = new SmartAjax({'url':'/main_user/verify_device_id','protocol':'GET','json_data':{'url':url},'success_callback':set_url_field});
        smart_ajax.get_update();
      }      
    });  

})

  function stop_scan(){
    $('#video').css('display','none');
    scanner.stop();
  }

  function set_url_field(res){
    if (res && res.success){
      $('#id_gsm-url').val(res.url);
      $('#description').text('Device has been attached!');
      $('#description').css('color','#138622');
      $('#scanbutton').text('Scan QR Code Again');
      // alert('Device has been attached!');
    }
    else{
      alert(res.error);
      $('#acs_module').prop("checked", false);
      $('#acs_module').trigger("change");
      $('#description').text('Scan the QR code to attach ACS Module:');
      $('#description').css('color','black');
      $('#scanbutton').text('Scan QR Code');

    }
    $('#loader').css('display','none');
    $('.btn_scan').css('display','block');
  }


function start_scanning() {
  // scanner.mirror=false;
  _iOSDevice = !!navigator.platform.match(/iPhone|iPod|iPad/);
  $('.btn_scan').css('display','none');
  $('#video').css('display','');
  $('#description').text('Scan the QR code to attach ACS Module:');
  $('#description').css('color','black');
  $('#scanbutton').text('Scan QR Code');
  $('#id_gsm-url').val('');
  try{
    Instascan.Camera.getCameras().then(cameras => {
      if(cameras.length > 0){
          if(cameras.length > 1){
              if(_iOSDevice){
                  scanner.start(cameras[0]);
                  return;
              }
              scanner.start(cameras[1]);
          }else{
              scanner.start(cameras[0]);
          }

      } else {
          alert("Please enable Camera!");
      }
    });

  }catch(e){
    alert(e);
  }
}
