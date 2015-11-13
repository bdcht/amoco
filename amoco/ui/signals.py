from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

try:
    import blinker
    has_blinker = True

except ImportError:
    logger.info('blinker package not found, no ui.signals defined')
    has_blinker = False
