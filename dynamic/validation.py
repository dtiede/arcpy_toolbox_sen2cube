import arcpy
import sys
import os
import json
import requests
import logging
from arcgis.geometry import Point, Polyline, Polygon, Geometry
from arcgis.gis import GIS
from arcgis.geocoding import geocode
from arcgis.geometry import lengths, areas_and_lengths, project
import pandas as pd
import requests_oauthlib
import oauthlib
import time
import urllib
from urllib.request import urlopen
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
from oauthlib.oauth2 import InvalidGrantError, LegacyApplicationClient, OAuth2Token, \
    UnauthorizedClientError
from requests import Response
from requests_oauthlib import OAuth2Session


def fetch_token(username: str, password: str,
                auth_token_url: str,
                auth_client_id: str,
                ) -> OAuth2Token:
    """
    Get OAuth token from auth_token_url and store in config_path_tokenfile
    :return: OAuth2Token with session information or None if any error
    """

    try:
        client: Final[LegacyApplicationClient] = LegacyApplicationClient(client_id=auth_client_id)
        with OAuth2Session(client=client) as oauth_session:
            token: Final[OAuth2Token] = oauth_session.fetch_token(
                token_url=auth_token_url,
                client_id=auth_client_id,
                username=username,
                password=password
            )
            # arcpy.AddMessage(f"Login successful. Got token: {token}")
            return token
    except UnauthorizedClientError:
        arcpy.AddErrorMessage(
            f"Authorisation failed for token url {auth_token_url} as client {auth_client_id}.",
            exc_info=True,
        )
    except InvalidGrantError as e:
        arcpy.AddErrorMessage(f"Login failed. Reason {str(e)}", exc_info=False)
    except Exception:
        arcpy.AddErrorMessage(
            f"Unknown error on authentication for token url {auth_token_url} as client {auth_client_id}.",
            exc_info=True, )

class ToolValidator:
    # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties.
        # This gets called when the tool is opened.
        return


    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before
        # standard validation.
        auth_token_url = "https://auth.sen2cube.at/realms/sen2cube-at/protocol/openid-connect/token"
        auth_client_id = "iq-web-client"
        # fb_list = 'https://api.sen2cube.at/v1/factbase?fields[factbase]=title'
        fb_list = 'https://api.sen2cube.at/v1/factbase'
        kb_list = 'https://api.sen2cube.at/v1/knowledgebase'


        if not self.params[2].value == True:
            self.params[3].enabled = False
            self.params[4].enabled = False
            self.params[5].enabled = False
            self.params[6].enabled = False
            self.params[7].enabled = False
            self.params[8].enabled = False
            self.params[9].enabled = False
            self.params[10].enabled = False

        if self.params[2].value == True:
            username = self.params[0].value
            password = self.params[1].value

            token_text = fetch_token(username, password, auth_token_url, auth_client_id)
            if token_text:
                # hide login parameters
                self.params[0].enabled = False
                self.params[1].enabled = False
                self.params[2].enabled = False

                entries = []

                # getting factbase list
                headers = {'Authorization': 'Bearer {}'.format(token_text['access_token'])}
                with requests.Session() as s:
                    s.headers.update(headers)
                    result = s.get(fb_list).json()

                    for i in range(4):
                        if result['data'][i]['attributes']['status'] == "OK":
                            entries.append(result['data'][i]['attributes']['title'])

                    self.params[3].filter.list = entries
                    self.params[3].enabled = True

        if self.params[3].altered:
            titles = []
            # getting knowledgebase list
            headers = {'Authorization': 'Bearer {}'.format(token_text['access_token'])}
            with requests.Session() as s:
                s.headers.update(headers)
                result1 = s.get(kb_list).json()

                length = len(result1['data'])

                for j in range(length):
                    titles.append(result1['data'][j]['attributes']['title'])

                self.params[4].filter.list = titles



            self.params[4].enabled = True
            self.params[5].enabled = True
            self.params[6].enabled = True
            self.params[7].enabled = True
            self.params[8].enabled = True
            self.params[9].enabled = True
            self.params[10].enabled = True

            """            
            factbase = self.params[3].value
            for i in range(4):
                if result['data'][i]['attributes']['title'] == factbase:
            
            # Date Range Check
            # format in JSON e.g. 2021-01-28
            start = result['data'][i]['attributes']['dateStart']
            end = result['data'][i]['attributes']['dateEnd']"""


        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        return

    # def isLicensed(self):
    #     # set tool isLicensed.
    # return True