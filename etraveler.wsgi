import sys 
sys.path.insert(0, '/var/www/html/etraveler')

from DataApp import app as application
application.secret_key = 'fc6908cce72e555c4ba2384e6a3a08dc'
