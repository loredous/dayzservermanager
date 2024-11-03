
from unittest.mock import mock_open, patch
from models import DayzServerConfig


MOCK_CONFIG_FILE = """
global:
  base_path: C:\Program Files (x86)\Steam\steamapps\common\DayZServer
  restart_time: 240
  cpu: 2
servers:
  - server_name: cherno_test
    name: Cherno DayZ Server
    port: 2331
    config_file: serverDZ_test.cfg
    executable: DayZServer_x64_test.exe
    profiles: C:\Program Files (x86)\Steam\steamapps\common\DayZServer\config_chernotest
    mods:
      - BaseBuildingPlus
      - CF
      - VanillaPlusPlusMap
      - VPPAdminTools
      - Code Lock
      - AmmoStackBullet
      - ZombieRunOverSound
      - Easy Signs [by Cl0ud]
      - PristineRepair+
      - UsefulSuppressors
      - Loot Barrel Transfer
      - InventoryInCaar
      - Gas-Pump-Refueling
      - Unlimited Stamina
      - OP_BaseItems
      - Solar Panel Power System
      - DayZ-Dog
      - SchanaModGlobalChat
      - SchanaModParty
      - MuchFramework
      - MuchStuffPack
      - Ear-Plugs
      - Powerstrip
      - RaG_BaseItems
      - Combinable Items
      - RaG_Hunting_Cabin
      - BodyBags
      - SIX-DayZ-Auto-Run
    extra_args:
      - dologs
      - adminlog
      - netlog
      - freezecheck
"""

@patch("builtins.open", new_callable=mock_open, read_data=MOCK_CONFIG_FILE)
def test_create_from_file(mock_file):
    MOCK_FILENAME = "myconfig.yaml"
    result = DayzServerConfig.from_config_file("")

    assert isinstance(result, list)
    assert len(result) == 1
    assert all([isinstance(item,DayzServerConfig) for item in result])