from typing import List
import requests
import time
from dotenv import load_dotenv
import os


class RequestFailedException(Exception):
    pass


# make dictionary of variables, then do <VARIABLE_NAME> in your url. Sender will
# send a regular request, but replace your variables before sending the request to the URL
def send_request(url: str, variables=dict(), headers=dict(), method="GET") -> requests.Response:
    uarel = url
    # get api key or something
    url = process_url(url, variables)
    # send the req
    if method == "GET":
        response = requests.get(url=url, headers=headers)
        # Logger.verbose("sending GET to " + url)
    else:
        response = requests.post(url=url, headers=headers)
        # Logger.verbose("sending POST to " + url)

    if not response.ok:
        raise RequestFailedException("Failed " + url + ", code " + str(response.status_code))
    return response


def process_url(url, variables):
    for key in variables:
        url = url.replace("<" + key + ">", variables[key])
    return url

