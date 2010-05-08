import os
import urllib
import urllib2
import cookielib

users_email_address = "username@gmail.com"
users_password      = "password"
my_app_name = "wattcher"
target_authenticated_google_app_engine_uri = 'http://wattcher.appspot.com/report'



# we use a cookie to authenticate with Google App Engine
#  by registering a cookie handler here, this will automatically store the 
#  cookie returned when we use urllib2 to open http://currentcost.appspot.com/_ah/login
cookiejar = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
urllib2.install_opener(opener)

#
# get an AuthToken from Google accounts
#
auth_uri = 'https://www.google.com/accounts/ClientLogin'
authreq_data = urllib.urlencode({ "Email":   users_email_address,
                                  "Passwd":  users_password,
                                  "service": "ah",
                                  "source":  my_app_name,
                                  "accountType": "HOSTED_OR_GOOGLE" })
auth_req = urllib2.Request(auth_uri, data=authreq_data)
auth_resp = urllib2.urlopen(auth_req)
auth_resp_body = auth_resp.read()
# auth response includes several fields - we're interested in 
#  the bit after Auth= 
auth_resp_dict = dict(x.split("=")
                      for x in auth_resp_body.split("\n") if x)
authtoken = auth_resp_dict["Auth"]

#
# get a cookie
# 
#  the call to request a cookie will also automatically redirect us to the page
#   that we want to go to
#  the cookie jar will automatically provide the cookie when we reach the 
#   redirected location

def sendreport(sensornum, watt):
    # this is where I actually want to go to
    serv_uri = target_authenticated_google_app_engine_uri + "?watt="+str(watt)+"&sensornum="+str(sensornum)

    serv_args = {}
    serv_args['continue'] = serv_uri
    serv_args['auth']     = authtoken
    
    full_serv_uri = "http://wattcher.appspot.com/_ah/login?%s" % (urllib.urlencode(serv_args))

    serv_req = urllib2.Request(full_serv_uri)
    serv_resp = urllib2.urlopen(serv_req)
    serv_resp_body = serv_resp.read()

    # serv_resp_body should contain the contents of the 
    #  target_authenticated_google_app_engine_uri page - as we will have been 
    #  redirected to that page automatically 
    #
    # to prove this, I'm just gonna print it out
    print serv_resp_body
