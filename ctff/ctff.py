
from typing import Callable
import functools

import httpx

registry = set()

def register_flag(flag_name):
  registry.add(flag_name)

async def register_flags_with_server(server_url, application_identity):
  flags_data = {"flags": list(registry)}
  # get auth for this instance
  async with httpx.AsyncClient() as client:
    authentication = "something"
    url = f"{server_url}/{application_identity}/register"
    r = await client.post(url, json=flags_data, headers={"authentication": authentication})

    return r.status_code


def lookup_flag(flag_name: str) -> bool:
  # do cool magic
  print(f"Looking up, the flag: {flag_name}")
  return True

def FeatureFlaggerMiddleware():
  pass

def FeatureFlagDecorator(flag_name):
  # register flag_name
  print(f"Registering flag: {flag_name}")
  register_flag(flag_name)

  def inner(fn: Callable) -> Callable:
      @functools.wraps(fn)
      def decorated(*args, **kwargs):
        kwargs[flag_name] = lookup_flag(flag_name)
        return fn(*args, **kwargs)
      return decorated
  
  return inner

featureflag = FeatureFlagDecorator
