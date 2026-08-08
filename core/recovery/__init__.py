from .manager import recovery_manager
from .exchange import ExchangeRecovery
from .signal import SignalRecovery
from .dca import DCARecovery
from .grid import GridRecovery
from .hunter import HunterRecovery

recovery_manager.register(ExchangeRecovery())
recovery_manager.register(SignalRecovery())
recovery_manager.register(DCARecovery())
recovery_manager.register(GridRecovery())
recovery_manager.register(HunterRecovery())
