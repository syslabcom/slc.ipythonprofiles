# -*- coding: utf-8 -*-
from IPython.core.interactiveshell import InteractiveShell
from oira.statistics.deployment.metabase import OiraMetabase_API
import os

args = {
    "metabase_host": os.environ["METABASE_HOST"],
    "metabase_port": os.environ["METABASE_PORT"],
    "metabase_user": os.environ["METABASE_USER"],
    "metabase_password": os.environ["METABASE_PASSWORD"],
}

api_url = "http://{args[metabase_host]}:{args[metabase_port]}".format(args=args)
mb = OiraMetabase_API(
    api_url, args["metabase_user"], args["metabase_password"].replace("\\", "\\\\")
)  # XXX what's with the backslash?

ip = InteractiveShell.instance()
ip.user_ns["mb"] = mb
