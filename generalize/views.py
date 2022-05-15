from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect
import json
from datetime import datetime
from django.db.models import F
from django.forms import model_to_dict
from django.conf import settings
import urllib.parse as cookie_parse
import base64
import logging

logger = logging.getLogger(__name__)

class CookieParser:
    def __init__(self, *args, **kwargs):
        return super(CookieParser,self).__init__()
    def cookie_parser(self, cookie):
        if not cookie is None:
            cookie = cookie.replace("'", '"')
            cookie_parsed = cookie_parse.unquote(cookie)
            try:
                return json.loads(cookie_parsed)
            except:    
                return cookie_parsed
        return None    

def printf(*args):
    if settings.DEBUG:
        p = ''
        sep = ''
        for a in args:
            p += sep + str(a)
            sep = ' '
        print(p)
        logger.debug(p)

def loggerf(*args):
    p = ''
    sep = ''
    for a in args:
        p += sep + str(a)
        sep = ' '
    if settings.DEBUG:
        print(f'Logger : {p}')
    else:
        logger.debug(p)           

class Generalize(CookieParser):
    def __init__(self,request):
        self.request=request

    def request_get(self,get_val,typ, default=None):
        try:
            if self.request.method == 'POST':
                if typ == 'list':
                    return self.request.POST[get_val]
                val = self.request.POST.get(get_val)
            elif self.request.method == 'GET':
                if typ == 'list':
                    return self.request.GET[get_val]
                val = self.request.GET.get(get_val)
            if val==None:
                return default
            if typ=='str':
                return str(val)
            elif typ=='int':
                return int(val)
            elif typ=='float':
                return float(val)
            elif typ=='bool':
                return bool(val)

        except Exception as e:
            loggerf('Generalize().request_get() Error: ',e)
            return default

    def retrive_data(self,key,typ=None,default=None):
        try:
            try:
                if self.request.session.has_key(key):
                    session_val = 	self.request.session.get(key)
                else:
                    session_val = None
            except Exception as e:
                loggerf('Generalize().retrive_data() Error1: ',e,key)
                session_val=None
                pass
            try:
                cookie_val		=	self.cookie_parser(self.request.COOKIES.get(key) or '')
            except Exception as e:
                loggerf('Generalize().retrive_data() Error2: ',e,key)
                cookie_val=None
                pass

            valid_data_arr 	= []
            for data in [session_val,cookie_val]:
                if not data is None and data!='':
                    valid_data_arr.append(data)
            if session_val is None and valid_data_arr[0]:        
                self.request.session[key] = valid_data_arr[0]
            if typ and valid_data_arr[0] and valid_data_arr[0]!='None':
                if typ=='int':
                    return int(valid_data_arr[0])
                elif typ=='str':
                    return str(valid_data_arr[0])
                elif typ=='float':
                    return float(valid_data_arr[0])
                elif typ=='bool':
                    return bool(valid_data_arr[0])
            return valid_data_arr[0] or default

        except Exception as e:
            loggerf('Generalize().retrive_data() Error3: ',e,key)
            return default      

    def store_data(self,response,key_arr,val_arr,default_storage='session'):
        try:
            if type(key_arr)==list:
                for i in range(0,len(key_arr)):
                    if default_storage=='both' or default_storage=='cookie':
                        response.set_cookie(key_arr[i],val_arr[i])
                    if default_storage=='both' or default_storage=='session':
                        self.request.session[key_arr[i]]=val_arr[i]
                        self.request.session.save() 
            elif type(key_arr)==str:
                if default_storage=='both' or default_storage=='cookie':
                    response.set_cookie(key_arr,val_arr)
                if default_storage=='both' or default_storage=='session':      
                    self.request.session[key_arr]=val_arr
                    self.request.session.save() 
            return True
        except Exception as e:
            loggerf('Generalize().store_data() Error: ',e)
            return False

    def clear_data(self,response,key_arr,default_storage='session'):
        try:
            if type(key_arr)==list:
                for i in range(0,len(key_arr)):
                    if default_storage=='both' or default_storage=='cookie':
                        response.delete_cookie(key_arr[i])
                    if default_storage=='both' or default_storage=='session':
                        try:
                            del self.request.session[key_arr[i]]
                        except KeyError:
                            pass
            elif type(key_arr)==str:
                if default_storage=='both' or default_storage=='cookie':
                    response.delete_cookie(key_arr)
                if default_storage=='both' or default_storage=='session':    
                    try:
                        del self.request.session[key_arr]
                    except KeyError:
                        pass
            return True
        except Exception as e:
            loggerf('Generalize().clear_data() Error: ',e)
            return False

    def save_redirect(self,url,key_arr,val_arr,default_storage='session'):
        response =  redirect(url)
        self.store_data(response,key_arr,val_arr,default_storage)
        return response

    def save_render(self,template_name,context,key_arr,val_arr,default_storage='session'):
        response =  render(self.request,template_name,context)
        self.store_data(response,key_arr,val_arr,default_storage)
        return response

    def save_HttpResponse(self,context,key_arr,val_arr,default_storage='session'):
        response =  HttpResponse(json.dumps(context))
        self.store_data(response,key_arr,val_arr,default_storage)
        return response

