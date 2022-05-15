$(document).ready(function(){
	function UserToVictimPath(json_data) {
		if ('url' in json_data && json_data.url!=undefined)
			window.location.href = json_data.url;
	}
	function RedirectToMapPage(lat_lng){
		var url = 	new URL(window.location.href);
		sm_ajx 	= 	new SmartAjax({
        url             :   '/notipush/redirect_to_map',
        protocol        :   'GET',
        json_data       :   {
        						eid 		: 	url.searchParams.get('eid'),
        						user_lat 	: 	lat_lng['lat'], 
        						user_lng 	: 	lat_lng['lng'],
        					},
        time_out_msg    :   'Please relaod the page again!',
        success_callback: 	UserToVictimPath,
 		});
		t = sm_ajx.get_update();
	}
	GetUserLatLng(RedirectToMapPage);
});