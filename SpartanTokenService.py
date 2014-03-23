#!/usr/bin/python

import re
import json
import random
import urllib
import requests

from requests import Request, Session
from requests.cookies import RequestsCookieJar

MS_LOGIN = "https://logSpartanTokenService.pyin.live.com/login.srf?id=2"
WAYPOINT_GATEWAY = "https://www.halowaypoint.com/oauth/signin?returnUrl=https%3a%2f%2fwww.halowaypoint.com%2fen-us&locale=en-US"
WAYPOINT_REGISTER_URL = "https://settings.svc.halowaypoint.com/RegisterClientService.svc/spartantoken/wlid?_={0}"
SPARTAN_TOKEN_GENERATOR = "https://app.halowaypoint.com/oauth/spartanToken"
URL_TO_SCRAPE = "https://login.live.com/oauth20_authorize.srf?client_id=000000004C0BD2F1&scope=xbox.basic+xbox.offline_access&response_type=code&redirect_uri=https://www.halowaypoint.com/oauth/callback&state=https%253a%252f%252fwww.halowaypoint.com%252fen-us&locale=en-US&display=touch"
URL_TO_POST = "https://login.live.com/ppsecure/post.srf?client_id=000000004C0BD2F1&scope=xbox.basic+xbox.offline_access&response_type=code&redirect_uri=https://www.halowaypoint.com/oauth/callback&state=https%253a%252f%252fwww.halowaypoint.com%252fen-us&locale=en-US&display=touch&bk=1383096785"

EMAIL = "PLACE_EMAIL_HERE"
PASSWORD = "PLACE_PASSWORD_HERE"

def get_spartan_token():
    # Get the First Cookies
    cookie_container = RequestsCookieJar()
    first_response = requests.get(URL_TO_SCRAPE)
    body = first_response.text.encode('utf-8', 'ignore')
    for cookie in first_response.cookies: cookie_container.set_cookie(cookie)

    # Get the PPFT
    ppft_regex = re.compile("name=\"PPFT\".*?value=\"(.*?)\"")
    ppft_match = re.findall(ppft_regex, body)
    assert len(ppft_match) == 1
    ppft = ppft_match[0]

    # Prepare the login to Xbox
    ppsx = "Pass"
    query = "PPFT={ppft}&login={email}&passwd={password}&LoginOptions=3&NewUser=1&PPSX={ppsx}&type=11&i3={random}&m1=1680&m2=1050&m3=0&i12=1&i17=0&i18=__MobileLogin|1".format(
        ppft = ppft, email = urllib.quote(EMAIL), password = PASSWORD, ppsx = ppsx, random = random.randint(15000, 50000))
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Host": "login.live.com", "Expect": "100-continue", "Connection": "Keep-Alive"}

    # Stream the login to xbox
    s = Session()
    login_request = Request('POST', URL_TO_POST, headers = headers, data = query, cookies = cookie_container)
    prepped = s.prepare_request(login_request)
    login_response = s.send(prepped, stream = True, allow_redirects = False)
    for cookie in login_response.cookies: cookie_container.set_cookie(cookie)
    if "Location" not in login_response.headers: return None
    next_location = login_response.headers['Location']

    # Get Waypoint Cookies and Headers
    waypoint_response = requests.get(next_location, allow_redirects = False)
    if "WebAuth" not in waypoint_response.cookies: return None
    for cookie in waypoint_response.cookies: cookie_container.set_cookie(cookie)

    # Get the Spartan Token
    headers = {"UserAgent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17"}
    token_response = requests.get(SPARTAN_TOKEN_GENERATOR, headers = headers, cookies = cookie_container)
    spartan_token = token_response.text
    spartan_token = json.loads(spartan_token)["SpartanToken"]

    return spartan_token