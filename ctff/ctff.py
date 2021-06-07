import os
from typing import Callable
import functools
import yaml

import httpx


async def server_lookup_flag(server_url, application_identity, flag_name):
    async with httpx.AsyncClient() as client:
        # TODO: Something about auth
        url = f"{server_url}/{application_identity}/flags/{flag_name}"
        resp = await client.get(url)
        # TODO: Error handling
        return resp.json()["state"]


async def local_lookup_flag(local_path, flag_name):
    flag_file_path = os.path.join(local_path, flag_name)
    if not os.path.isfile(flag_file_path):
        return False
    with open(flag_file_path) as flag_file:
        config = yaml.safe_load(flag_file)

        if type(config) is bool:
            return config
        elif type(config) is dict:
            return config["base"]
    return False


class FeatureFlagger:
    server_url: str
    application_identity: str

    flag_registry = set()

    lookup_chain = []

    def __init__(
        self, server_url: str, application_identity: str, local_backup: str = None
    ) -> None:
        self.server_url = server_url
        self.application_identity = application_identity

        self.lookup_chain = [
            functools.partial(
                server_lookup_flag, self.server_url, self.application_identity
            )
        ]
        if local_backup is not None:
            self.lookup_chain.append(functools.partial(local_lookup_flag, local_backup))

    def register_flag(self, flag_name):
        self.flag_registry.add(flag_name)

    async def register_flags_with_server(self) -> bool:
        flags_data = {"flags": list(self.flag_registry)}
        # get auth for this instance
        async with httpx.AsyncClient() as client:
            # TODO: Authentication
            url = f"{self.server_url}/{self.application_identity}/register"
            resp = await client.post(url, json=flags_data)

            return resp.status_code == 200

    async def lookup_flag(self, flag_name) -> bool:
        # consider logging errors
        for lookup in self.lookup_chain:
            try:
                return await lookup(flag_name)
            except:
                pass
        return False

    def flag(self, flag_name):
        """
        Decorates a function for including the feature flag name in the key-value args to the fucntion.
        """
        self.register_flag(flag_name)

        def inner(fn: Callable) -> Callable:
            @functools.wraps(fn)
            async def decorated(*args, **kwargs):
                kwargs[flag_name] = await self.lookup_flag(flag_name)
                return fn(*args, **kwargs)

            return decorated

        return inner
