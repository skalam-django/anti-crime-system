sngsms = {
	
}
twilio = {
	
}

# PROVIDER_PRIORITY = OrderedDict()
PROVIDER_PRIORITY = {
	'sngsms' : {
				'CRITICAL_TIMEOUT' 	:	3,
				'FAILURE_CONST' 	: 	3, # per day
				'key' 				:	'45D3FEABC3D3D8',
				'campaign' 			:	7995,
				'routeid' 			:	30,
	}, 
	'twilio' : {
				'CRITICAL_TIMEOUT' 	:	2,
				'FAILURE_CONST' 	: 	2,
				'account_sid' 		:	'AC2498cb7a628cd3aae3bc8e4015141318',
				'auth_token'		:	'79d4465f58c619ebe036004394900b50',
	},
}