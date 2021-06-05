
from typing import Callable
import functools

import httpx

class FeatureFlagger():
  server_url: str
  application_identity: str

  flag_registry = set()
  default_http_args = {}

  def __init__(self, server_url: str, application_identity: str) -> None:
      self.server_url = server_url
      self.application_identity = application_identity

  def register_flag(self, flag_name):
    self.flag_registry.add(flag_name)

  async def register_flags_with_server(self) -> bool:
    flags_data = {"flags": list(self.flag_registry)}
    # get auth for this instance
    async with httpx.AsyncClient() as client:
      #TODO: Authentication
      url = f"{self.server_url}/{self.application_identity}/register"
      resp = await client.post(url, json=flags_data)

      return resp.status_code == 200

  async def lookup_flag(self, flag_name) -> bool:
    async with httpx.AsyncClient(**self.default_http_args) as client:
      #TODO: Something about auth
      url = f"{self.server_url}/{self.application_identity}/flags/{flag_name}"
      resp = await client.get(url)
      # TODO: Error handling
      return resp.json()["state"]

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
