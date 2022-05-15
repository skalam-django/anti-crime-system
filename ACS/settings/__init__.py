import sys,os

if os.environ.get('SERVER') is None or os.environ.get('SERVER').lower()=='local':
    from ACS.settings.local import * 
elif os.environ.get('SERVER').lower()=='dev':
    from ACS.settings.dev import * 
elif os.environ.get('SERVER').lower()=='prod':
    from ACS.settings.prod import *     

print(f"Running: {SERVER} server")

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise
create_dir(MEDIA_ROOT)


print(f"**** DEBUG STATE **** : {DEBUG}")
print(f"**** SERVICES STATE **** : {SERVICES}")
print(f"**** DATABASE HOST **** : {DATABASES['default']['HOST']}")
print(f"**** DATABASE NAME **** : {DATABASES['default']['NAME']}")
print(f"**** STATIC_VERSION **** : {STATIC_VERSION}")

if os.environ.get('PRODUCTION') is not None and os.environ.get('PRODUCTION')=='True':
	sys.stdout = open(os.devnull, 'w')
