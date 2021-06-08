
import logging
from fastapi import FastAPI

logger = logging.getLogger("app")

from ctff import FeatureFlagger 

application_identity = "ctff-example-featureflags"

app = FastAPI(
  title="CTFF python example"
)
features = FeatureFlagger("http://localhost:9001", application_identity)

# app.add_middleware(FeatureFlaggerMiddleware, settings={})

@app.on_event("startup")
async def startup():
  logger.info("Application startup")
  await features.register_flags_with_server()


@app.on_event("shutdown")
async def shutdown():
  logger.info("Application shutdown")

@app.get("/")
async def root():
  return {"message": "Hello World", "app_color": get_app_color()}


@features.flag("use_new_color")
def get_app_color(use_new_color = False):
  if use_new_color:
    return "Orange"
  else:
    return "Pink"

# Get feature flag state:
# curl http://localhost:9001/ctff-example-featureflags/flags/use_new_color

# Set feature flag state:
# curl -XPOST --data "on" http://localhost:9001/ctff-example-featureflags/flags/use_new_color
