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

    def __add_session__(self, mode, hash_val=None, **aiohttp_session_kwargs):
        """
        Adds a session to the session manager if it is necessary.

        It selects the mode (async or sync, aiohttp or requests) and checks
        if there is a session already active for the specific mode and hash
        value. If it doesn't exist it adds the session, if it exist it does
        nothing.

        The hash value is used to represent the information passed in the
        header.

        aiohttp_session_kwargs are needed for async session since requests
        pacakge session doesn't have initialization params.
        base_url is removed from aiohttp params

        Parameters
        ----------
        mode : str, Literal['sync', 'async']
            The mode of the session, sync or async.
        hash_val : str, optional
            The hash value of the headers data. The default is None.
        **aiohttp_session_kwargs: optional
            The params used to build the session for aiohttp.

        Returns
        -------
        None.

        """
        if mode == 'sync':
            # If hash is None then it is a session where headers are
            # irrelevant
            if hash_val is None:
                # We check if the session already exists
                if self.__sessions[mode]['no-metadata'] is None:
                    self.__sessions[mode]['no-metadata'] = r.Session()
            # In case hash_val is not None, the session is added as one with
            # with custom params
            else:
                try:
                    self.__sessions[mode]['custom-metadata'][hash_val]
                except KeyError:
                    self.__sessions[mode]['custom-metadata'][hash_val] = (
                        r.Session()
                    )  # Between () for multiline, to avoid 79 cols limit.
        elif mode == 'async':
            if hash_val is None:
                if self.__sessions[mode]['no-metadata'] is None:
                    self.__sessions[mode]['no-metadata'] = (
                        aiohttp.ClientSession()
                    )  # Between () for multiline, to avoid 79 cols limit.
            else:
                try:
                    self.__sessions[mode]['custom-metadata'][hash_val]
                except KeyError:
                    kwargs = dict(aiohttp_session_kwargs)
                    # dict() makes a copy, to not interfere on the original.
                    kwargs.pop('base_url', None)
                    # None val prevent the KeyError if base_url is not present.
                    self.__sessions[mode]['custom-metadata'][hash_val] = (
                        aiohttp.ClientSession(**kwargs)
                    )  # Between () for multiline, to avoid 79 cols limit.
        return None

    def __select_session__(self, mode, hash_val=None,
                           **aiohttp_session_kwargs):
        """
        Returns the session of your choice and creats one if it doesn't exists.

        **aiohttp_session_kwargs is used to build the session as specified in
        the add_session method.

        Parameters
        ----------
        mode : str, Literal['sync', 'async']
            The mode of the session, sync or async.
        hash_val : str, optional
            The hash value of the headers data. The default is None.
        **aiohttp_session_kwargs: optional
            The params used to build the session for aiohttp.

        Returns
        -------
        Session
            The session object, wether sync or async.

        """
        self.__add_session__(mode, hash_val, **aiohttp_session_kwargs)
        if hash_val is None:
            return self.__sessions[mode]['no-metadata']
        else:
            return self.__sessions[mode]['custom-metadata'][hash_val]

    def __get_header_data__(self, mode, dictionary):
        """
        Gets the data from the header params of the request and pass it to str.

        Parameters
        ----------
        mode : Literal['sync', 'async']
            Mode of the request, async or sync.
        dictionary : The Kwargs of the request.
            The Keyword arguments of the request.
                - Requests package if sync mode
                - Aiohttp if async mode.

        Returns
        -------
        new_dict : dict
            Header data of request.
            It returns an empty dict if there is no header data.

        """
        request_header_params = [
            'auth',
            'cookies',
            'headers',
        ]
        aiohttp_header_params = [
            'auth',
            'cookies',
            'headers'
        ]
        if mode == 'sync':
            keywords = request_header_params
        elif mode == 'async':
            keywords = aiohttp_header_params

        # We rebuild the dictionary just to have it sorted in order to get the
        # same hash each time.
        new_dict = dict()
        for k in keywords:
            try:
                new_dict[k] = dictionary[k]
            except KeyError:
                continue
        return new_dict

    def __dict_to_str__(self, dictionary):
        """
        Transform a dict to str with specified format.

        Parameters
        ----------
        dictionary : dict
            Dict to pass to string

        Returns
        -------
        dict as str.

        """
        data_str = """"""
        for k, v in dictionary.items():
            if isinstance(v, dict):
                data_str += self.__dict_to_str__(v)
            else:
                data_str += f'{k} {str(v)}'
                # There is no need for clean readable format, since it will
                # be used just to compute the hash.
        return data_str

    def __get_hash_value_of_dict__(self, dictionary):
        """
        Computes the hash value of the passed dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary to get the hash from.

        Returns
        -------
        hash_str : str
            7 first terms of SHA1 of the dictionary.
            Returns None if the dict is empty

        """
        if not bool(dictionary):
            return None
        hasher = h.sha1(usedforsecurity=False)
        hasher.update(self.__dict_to_str__(dictionary))
        hash_str = hasher.hexdigest()
        return hash_str[:7]

    def get_session(self, mode, **request_kwargs):
        """
        Gathers a session based on the url, the mode and the params.

        The gathered session will be sync or async based on the mode

        Parameters
        ----------
        mode : str, Literal[sync, async]
            The mode of the session, sync or async
        **request_kwargs : TYPE
            requests.Request kwargs if mode is sync
            aiohttp.Request kwargs if mode is async

        Returns
        -------
        session : requests.Session | aiohttp.Session
            Session of one of the packages requests or aiohttp.

        """
        header_data = self.__get_header_data__(mode, request_kwargs)
        hash_val = self.__get_hash_value_of_dict__(header_data)
        session = self.__select_session__(mode, hash_val)
        return session

    def get_all_sessions(self):
        "Returns teh private attribute sessions. The dict with the sessions."
        return self.__sessions

    async def __close_all_sessions_private__(self):
        for mode, data in self.__sessions.items():
            # mode is for sync, async start of the dict
            # data is always a dict
            for meta, data2 in data.items():
                # meta is no-metadata or custom-metadata
                # data2 could be None for no-metadata
                # or a session if it was initiated
                # or a dict for custom-metadata
                # in such case each val of the dict will be a session.
                if data2 is None:
                    continue
                elif isinstance(data2, dict):
                    for hash_val, sess in data2.items():
                        if mode == 'async':
                            await sess.close()
                        else:
                            sess.close()
                        print(f'{hash_val} ({mode}): was_closed.')
                else:
                    if mode == 'async':
                        await data2.close()
                    else:
                        data2.close()
                    print(f'no-metadata ({mode}): was_closed.')
        return None

    def close_all_sessions(self):
        'Closes all sessions.'
        # Since this function is meant to be run in the backgraound and when
        # the system decides and is not meant to be called by the user.
        asyncio.create_task(self.__close_all_sessions_private__())
        return None


class DomainManager():
    # The domain manager handles each of the requested domains and their
    # respective queues
    def __init__(self):
        self.__domains = dict()
        return None







SM = SessionManager()
SM.get_session('sync', url='https://www.ine.es/dyngs/DAB/index.htm?cid=1100', method='GET')
SM.get_session('async', url='https://www.ine.es/dyngs/DAB/index.htm?cid=1100', method='GET')

url = yarl.URL('https://www.ine.es/dyngs/DAB/index.htm?cid=1100')
b = yarl.URL(url)
