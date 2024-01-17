from pox.core import core
from .controller import BSSController

def launch (no_cookieguard=False):
  if no_cookieguard:
    BSSController.pox_cookieguard = False

  def _launch ():
    core.WebServer.set_handler("/bss/", BSSController, {}, True)
  core.call_when_ready(_launch, ["WebServer"], name = "bss")
