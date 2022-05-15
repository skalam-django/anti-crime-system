$(document).ready(function(){
	function HomePage(json_data) {
		console.log('json_data',json_data);
		if ('url' in json_data && json_data.url!=undefined)
			window.location.href = json_data.url;
	}
	function RedirectToHome(lat_lng){
		sm_ajx 	= 	new SmartAjax({
        url             :   '/main_user/get_location/',
        protocol        :   'POST',
        json_data       :   {
        						user_lat 	: 	lat_lng['lat'], 
        						user_lng 	: 	lat_lng['lng'],
        					},
        time_out_msg    :   'Please relaod the page again!',
        success_callback: 	HomePage,
 		});
		t = sm_ajx.get_update();
	}
	GetUserLatLng(RedirectToHome);
});