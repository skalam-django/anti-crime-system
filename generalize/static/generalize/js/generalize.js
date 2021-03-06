var lat_lng = [];
var map = new Object();
var d = 0;
var marker = new Object();
var args = new Object();
var latLng = new Object();
var lat = latLng.lat;
var lng = latLng.lng;
var shop_del_type;
var shop_lat;
var shop_lng;

$(document).ready(function(){


});

var SmartAjax = function(options)
{
    var vars = {
        url             :   undefined,
        protocol        :   'POST',
        dataType        :   'json',
        is_async        :   true,
        json_data       :   new Object(),
        interval        :   10000,
        inactive_mins   :   undefined,
        time_out        :   5,
        max_time_out    :   10,
        time_out_msg    :   undefined,
        once            :   true,
        success_callback: function(resultData) {
            console.log('SmartAjax() success_callback() resultData : ', resultData);
        },
        error_callback  : function(e){
            console.log('SmartAjax() error_callback() Error: ', e);
        },
    }
    root = this;
    var construct = function(options){
        $.extend(vars,options);

        if (vars.inactive_mins==undefined)
            vars.inactive_mins  =   (1.2*vars.interval)/(60*1000);

        root.started_at     =   new Date();
        root.restarted_at   =   new Date();
        root.st_time_out    =   new Date();
        root.reseted        =   true;
        var events          =   ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

        events.forEach(function(e) {
            document.addEventListener(e, resetTimeOut, true);
        });
    };

    root.get_update = function()
    {
        var durations = undefined;
        if (ajax()==false)
            console.log('SmartAjax() error_callback() Error: url not defined --> url: ',vars.url);    
        if(vars.once==false){
            var intv = setInterval(function(){
                var ed_time_out = new Date();
                if (document.hidden==false)
                    resetTimeOut();
                durations = (ed_time_out.getTime()-root.st_time_out.getTime())/(60*1000);
                if ((ed_time_out.getTime()-root.started_at.getTime())/(60*1000) > vars.max_time_out){
                    if(vars.time_out_msg!=undefined)
                        alert(vars.time_out_msg)
                    clearInterval(intv);
                }
                if ((ed_time_out.getTime()-root.restarted_at.getTime())/(60*1000) > vars.time_out){
                    if(vars.time_out_msg!=undefined){
                        alert(vars.time_out_msg)
                    }
                    clearInterval(intv);
                }
                if ((durations < vars.inactive_mins) || root.reseted==true){
                    root.reseted = false;
                    a = ajax();
                    if (a[0]==false)
                        console.log(`SmartAjax().ajax() Error: ${a[1]}`);
                }
            },vars.interval);
            return intv;
        }
    }
    var ajax = function()
    {
        try
        {
            if(vars.url==undefined || vars.url==null || vars.url==NaN)
                return [false,`url not defined --> url: ${vars.url}`];
            vars.json_data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                        type        : vars.protocol,
                        dataType    : vars.dataType,
                        async       : vars.is_async,
                        url         : vars.url,
                        data        : vars.json_data,
                        success     : vars.success_callback,
                        error       : vars.error_callback,
            });
            return [true];
        }
        catch(e)
        {
            return [false,e];
        }
    }

    var resetTimeOut = function()
    {
        root.st_time_out    =   new Date();
        root.restarted_at   =   new Date();
        root.reseted        =   true;
    }

    construct(options);
}


function init_marker(){

    google.maps.event.addListener(marker, 'dragend', function(e) {
        if (!this.getMap()) {
             this.unbindAll();
        }
        var v_lat = e.latLng.lat()
        var v_lng = e.latLng.lng()
        set_address_details_with_latlong({lat:v_lat,lng:v_lng})

    });
}

function set_default_marker_position(){
    try{
        if (navigator.geolocation)
            navigator.geolocation.getCurrentPosition(function(position){
               var latLng = {
                   lat: position.coords.latitude,
                   lng: position.coords.longitude
                };
                map.setCenter(latLng);
                set_address_details_with_latlong(latLng)
                set_marker_with_latlong(latLng)
                init_marker()
            },showError);
    }
    catch(e)
    {
        console.log('set_default_marker_position() Error: ',e);
    }
}

function GetUserLatLng(callback){
    try{
        if (navigator.geolocation)
            navigator.geolocation.getCurrentPosition(function(position){
            var latLng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
            };
            callback(latLng);
            },showError);
    }
    catch(e)
    {
        console.log('GetUserLatLng() Error: ',e);
    }    
}

function showError(error) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      alert("Request for Geolocation is Denied , Allow to Proceed Further")
      $('#address_close').click();
      break;
    case error.POSITION_UNAVAILABLE:
      alert("Location information is unavailable.")
      break;
    case error.TIMEOUT:
      alert("The request to get user location timed out.")
      break;
    case error.UNKNOWN_ERROR:
      alert("An unknown error occurred.")
      break;
  }
}

function set_marker_with_latlong(latLng){
    try{
        marker.setMap(null);
    }
    catch(e){
        console.log('showPosition() Error: ',e);
    }
    marker = new google.maps.Marker({
        position: latLng,
        title: '',
        map: map,
        draggable: true,
    });
    map.setZoom(15);
    map.panTo(marker.position);
}

function set_address_details_with_latlong(latLng,get_set=false,call_back) {
    lat_lng = [];
    lat_lng.push(latLng.lat);
    lat_lng.push(latLng.lng);
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'latLng': latLng }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK)
       return set_address_details(results,get_set,call_back);
    });
 }


function set_address_details(results,get_set=false,call_back){
    var address_types       = ['premise','street_number','route','neighborhood','sublocality_level_2','sublocality_level_3','sublocality_level_1','locality','administrative_area_level_1','country','postal_code','appartment_address','landmark'];
    var input_arr           = ['#street_address_1','#street_address_1','#street_address_1','#street_address_1','#street_address_2','#street_address_2','#street_address_2','#city','#state','#country','#pincode','#apartment_address','#landmark'];
    var formatted_address   = "";
    var types = [];
    var address_comp_dict = new Object;
    var type =[];
    var address_dict = new Object;
    var sep = '';
    for (var i in input_arr)
        $(input_arr[i]).val('');

    for (var i in results[0].address_components)
    {
        type=results[0].address_components[i].types
        delete type[type.indexOf('political')];
        for (var t in type)
            address_comp_dict[type[t]] = results[0].address_components[i].long_name;
    }
    var formatted_address = results[0].formatted_address;
    for(var typ in address_comp_dict)
    {
        if (address_types.includes(typ)==true)
        {
            var addr =address_dict[input_arr[address_types.indexOf(typ)]];
            if (addr==null || addr==undefined)
            {
                sep = '';
                addr='';
            }
            else
                sep = ',';
            address_dict[input_arr[address_types.indexOf(typ)]] =  addr+sep+address_comp_dict[typ];
        }
    }
    formatted_address_arr = formatted_address.split(',');
    formatted_address_arr = formatted_address_arr.slice(0,formatted_address_arr.length-3);
    if (address_dict['#street_address_2']==undefined || address_dict['#street_address_2']=='')
        address_dict['#street_address_2'] = formatted_address_arr[formatted_address_arr.length-2] + ',' + formatted_address_arr[formatted_address_arr.length-1];
    if (address_dict['#street_address_1']==undefined || address_dict['#street_address_1']=='')
    {
        address_dict['#street_address_1'] = '';
        var len = formatted_address_arr.length;
        sep = '';
        for (var i in Array(0,len-2))
        {
            address_dict['#street_address_1'] = address_dict['#street_address_1'] + sep + formatted_address_arr[i];
            sep = ',';
        }

    }


    get_apt_landmark(address_dict);

    if(get_set==false){
        for (var addr in address_dict)
            $(input_arr[input_arr.indexOf(addr)]).val(address_dict[addr]);        
    }
    else{
        call_back(address_dict);
    }
}


function get_apt_landmark(address_dict){
    var matched=false;
    var full_address = Cookies.get('full_address');
    if(full_address!=undefined && full_address!=null && full_address!='' && full_address!='{}' && full_address!='None' && full_address!='undefined'){
        full_address = JSON.parse(full_address);
        for (var addr in address_dict){
            var addr1 = addr.replace('#','');
            if(addr1=='apartment_address' || addr1=='landmark'){
                continue;
            }
            if(full_address[addr1]!=address_dict[addr]){
                matched=false;
                break;
            }else{
                matched=true;
            }
        }
        if (matched==true){
            var apartment_address = address_dict['#apartment_address'];
            var landmark = address_dict['#landmark'];
            if(apartment_address==undefined || apartment_address==null || apartment_address==''){
                apartment_address = full_address['apartment_address'];
                if(apartment_address!=undefined && apartment_address!=null && apartment_address!='undefined'){
                    address_dict['#apartment_address'] = apartment_address;
                }                
            }
            if(landmark==undefined || landmark==null || landmark==''){
                landmark =  full_address['landmark'];
                if(landmark!=undefined && landmark!=null && landmark!='undefined'){
                    address_dict['#landmark'] = landmark;
                }                
            }
            setTimeout(function(){
                validateForm('#location_form');
            },200);
            
        }else{
            Cookies.remove('full_address');
        }
    }
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: 12.96268, lng: 77.6489},
      zoom: 6,
      streetViewControl: false,
    });

    var bangalore_bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(12.864162, 77.438610),
        new google.maps.LatLng(13.139807, 77.711895));
    var india_bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(23.63936, 68.14712),
        new google.maps.LatLng(28.20453, 97.34466));

    
    var searchBox = new google.maps.places.SearchBox(document.getElementById('pac-input'),{bounds: india_bounds,strictBounds: true});

    google.maps.event.addListener(searchBox, 'places_changed', function() {
    searchBox.set('map', null);
    var places = searchBox.getPlaces();
    var bounds = india_bounds;
    var i, place;
    for (i = 0; place = places[i]; i++) {
        (function(place) {
         marker.bindTo('map', searchBox, 'map');
         google.maps.event.addListener(marker, 'map_changed', function(e) {
           if (!this.getMap()) {
             this.unbindAll();
           }
         });
         var v_lat = place.geometry.location.lat()
         var v_lng = place.geometry.location.lng()
         set_marker_with_latlong({lat:v_lat,lng:v_lng})
         init_marker()
         set_address_details_with_latlong({lat:v_lat,lng:v_lng})
         bounds.extend(place.geometry.location);
        }(place));
    }
//     map.fitBounds(bounds);
//     searchBox.set('map', map);
//     map.setZoom(Math.min(map.getZoom(),15));
   });
}





function deg2rad(deg) {
  return deg * (Math.PI/180)
}

function set_single_cookies(cookie_name,value)
{
    try
    {
        var inactive_minutes = 60 * 12;
        var expiry = 1/(24*(60/inactive_minutes));
        Cookies.set(cookie_name,value, { expires: expiry });
    }
    catch(e)
    {
        console.log('set_single_cookies() Error: ',e);
    }
}

function set_cookies(cookie_name_arr,value_arr)
{
    try
    {
        var inactive_minutes = Cookies.get('inactive_minutes');
        if (inactive_minutes==undefined)
            inactive_minutes= 60;
        inactive_minutes = parseInt(inactive_minutes);
        var expiry = 1/(24*(60/inactive_minutes));

        if (typeof(cookie_name_arr)=='object')
        {
            for (var i = 0; i < cookie_name_arr.length; i++)
            {
                var cookie_name = cookie_name_arr[i];
                var value       = value_arr[i];
                Cookies.set(cookie_name,value, { expires: expiry });
            }
        }
        else if (typeof(cookie_name_arr)=='string')
        {
            Cookies.set(cookie_name_arr,value_arr, { expires: expiry });
        }
    }
    catch(e)
    {
        console.log('set_cookies() Error: ',e);
    }
}

function clear_cookies(cookie_name)
{
    try
    {
        if (cookie_name == undefined || cookie_name=='' || cookie_name == 'all' || cookie_name == null || cookie_name == NaN)
        {
            Cookies.remove('cart_progress');
            Cookies.remove('cart_total');
            Cookies.remove('products_json');
            Cookies.remove('ind_shop_ul_id');
            Cookies.remove('viewed_cart');
            Cookies.remove('combo_packages');
            Cookies.remove('combo_packages_name');
            Cookies.remove('package_admin');
            Cookies.remove('channel_name');
            Cookies.remove('full_address');

        }
        else
            Cookies.remove(cookie_name);
    }
    catch(e)
    {
        console.log('clear_cookies() Error: ',e);
    }
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}


function add_decimals(value)
{
    try
    {
        value=$.trim(value);
        if (parseInt(value)==NaN || value==undefined || value=='')
            return 0;
        var value   = value.toString().match(/^-?\d+(?:\.\d{0,2})?/)[0];
        var val_arr = value.split('.');
        var int_val = val_arr[0];
        var dec_val = val_arr[1];
        if(parseInt(dec_val)<=0 || dec_val==undefined)
            return int_val+".00";
        return parseFloat(int_val+'.'+dec_val);
    }
    catch(e)
    {
        console.log('remove_decimals() Error: ',e);
        return 0;
    }
}



// var bangaloreBounds = new google.maps.LatLngBounds(
//     new google.maps.LatLng(12.864162, 77.438610),
//     new google.maps.LatLng(13.139807, 77.711895));

// var autocomplete = new google.maps.places.Autocomplete(this, {
//   bounds: bangaloreBounds,
//   strictBounds: true,
// });

// autocomplete.addListener('place_changed', function () {

// });