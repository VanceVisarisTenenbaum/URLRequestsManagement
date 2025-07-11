#
# Set shebang if needed
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 17:21:46 2025

@author: mano
"""

import pydantic as p
import requests as r
import asyncio
import aiohttp
import yarl
import typing as t
import annotated_types as at
import hashlib as h


def str_to_url(url: str) -> yarl.URL:
    # yarl already checks types
    return yarl.URL(url)


str_to_url('https://www.python.org/~guido?arg=1#frag')



class SessionManager():
    # The session manager, takes care of handling each available session
    # wether it is an async or sync requests session.
    def __init__(self):
        self.__sessions = {
            'sync': {
                'no-metadata': None,
                'custom-metadata': dict()
            },
            'async': {
                'no-metadata': None,
                'custom-metadata': dict()
            }
        }
        self.__sessions_initial_time = None
        """
        sessions is a private attribute. It is a dict used to manage all the
        sessions that might be needed.

        The structure is such to handle sync and async sessions independently.
            Each has the keys, "no-metadata" and "custom".
                no-metadata key would be a session to manage all requests that
                wont use any
                    cookie,
                    auth,
                    .
                    .
                    .
                while custom is used to handle the sessions that require any of
                the previously commented attributes.

        sessions_initial_time is an attribute used to store the starting time
        of the last request made.
        """
        return None

    def __add_session__(self, mode, **kwargs):
        hasher = h.sha1(usedforsecurity=False)
        h.update()
        return None

    def __get_header_data__(self, mode, dictionary):
        request_header_params = [
            'auth',
            'cookies',
            'headers',
        ]
        aiohttp_header_params = []

        if mode == 'sync':
            keywords = request_header_params
        elif mode == 'async':
            keywords = aiohttp_header_params

        new_dict = {key: dictionary[key] for key in keywords}
        return new_dict


class DomainManager():
    # The domain manager handles each of the requested domains
    def __init__(self):
        self.__domains = dict()
        return None



class RequestManager():
    # The session manager simply puts the session into different keys for
    # each host.
    def __init__(self):
        self.__sessions = {
            'sync': {
                'no-metadata': None,
                'custom': dict()
            },
            'async': {
                'no-metadata': None,
                'custom': dict()
            }
        }
        self.__sessions_initial_time = None
        """
        sessions is a private attribute. It is a dict used to manage all the
        sessions that might be needed.

        The structure is such to handle sync and async sessions independently.
            Each has the keys, "no-metadata" and "custom".
                no-metadata key would be a session to manage all requests that
                wont use any
                    cookie,
                    auth,
                    .
                    .
                    .
                while custom is used to handle the sessions that require any of
                the previously commented attributes.

        sessions_initial_time is an attribute used to store the starting time
        of the last request made.
        """
        return None

    def __add_session(self,
                      mode: t.Literal['sync', 'async'] = 'sync',
                      **kwargs
                      ) -> None:
        self.sessions
        return None

    def make_sync_request(self,
                          url: str | yarl.URL,
                          method: str = 'GET',
                          **kwargs
                          ) -> str:

        url = str_to_url(url)
        return None






url = yarl.URL('https://www.ine.es/dyngs/DAB/index.htm?cid=1100')
b = yarl.URL(url)
