from pox.core import core
from pox.web.webcore import SplitterRequestHandler, SplitRequestHandler, SplitThreadedServer
import os
import threading
from .controller import BSSController

log = core.getLogger()

def launch_jsonrpc (address='', port=8080, static=False, ssl_server_key=None,
            ssl_server_cert=None, ssl_client_certs=None,
            no_cookieguard=True,
            cors=False):
  if no_cookieguard:
    SplitterRequestHandler.pox_cookieguard = False
    assert no_cookieguard is True, "--no-cookieguard takes no argument"
    log.warn("Cookieguard disabled; this may be insecure.")

  # if str(cors).lower() == "permissive":
  #   SplitRequestHandler.ac_permissive_cors = True
  #   log.warn("Using permissive CORS policy; this may be insecure.")

  def expand (f):
    if isinstance(f, str): return os.path.expanduser(f)
    return f
  ssl_server_key = expand(ssl_server_key)
  ssl_server_cert = expand(ssl_server_cert)
  ssl_client_certs = expand(ssl_client_certs)

  httpd = SplitThreadedServer((address, int(port)), SplitterRequestHandler,
                              ssl_server_key=ssl_server_key,
                              ssl_server_cert=ssl_server_cert,
                              ssl_client_certs=ssl_client_certs)
  core.register("WebServer", httpd)
  httpd.set_handler("/", BSSController, {}, True)
  
  def run ():
    try:
      msg = "https" if httpd.ssl_enabled else "http"
      msg += "://%s:%i" % httpd.socket.getsockname()
      log.info("Listening at " + msg)
      httpd.serve_forever()
    except:
      pass
    log.info("Server quit")

  def go_up (event):
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

  def go_down (event):
    BSSController.shutdown()
    httpd.shutdown()

  core.addListenerByName("GoingUpEvent", go_up)
  core.addListenerByName("GoingDownEvent", go_down)

launch_jsonrpc()
