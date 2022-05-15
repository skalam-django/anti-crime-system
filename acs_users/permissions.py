from django.conf import settings

MODEL_PERMS =   {
                    
                    'token' :   {
                                    'add'       :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'authuser' : {
                                    'add'       :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]

                    },
                    'ipwhitelist':{
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'mainuser':{
                                    'add'       :   [settings.CLIENT_GROUPS[0][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[0][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'policestation':{
                                    'add'       :   [settings.CLIENT_GROUPS[3][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[3][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'gsm_device':{
                                    'add'       :   [settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    # 'change'    :   [settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]]
                    },
                    'rf_device':{
                                    'add'       :   [settings.CLIENT_GROUPS[2][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[2][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[2][0]]
                    },
                    'postalcode':{
                                    'add'       :   [settings.CLIENT_GROUPS[3][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[3][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'events':{
                                    'add'       :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'requestcancellation':{
                                    'add'       :   [settings.CLIENT_GROUPS[0][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[0][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                    'eventhistory':{
                                    'add'       :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    'change'    :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]],
                                    'view'      :   [settings.CLIENT_GROUPS[0][0], settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0], settings.CLIENT_GROUPS[3][0]]
                    },
                }


