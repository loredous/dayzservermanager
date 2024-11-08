from typing import List
from dataclasses import dataclass, field
from subprocess import Popen, PIPE, DEVNULL, TimeoutExpired
from logging import getLogger, Logger, DEBUG,INFO
from time import sleep, time
from yaml import load, BaseLoader
from steam import SteamQuery


@dataclass
class DayzServerConfig:
    name: str
    server_name: str
    base_path: str
    config_file: str
    executable: str
    port: int
    steamquery_port: int
    restart_time: int
    profiles: str
    extra_args: List[str] = field(default_factory=list)
    mods: List[str] = field(default_factory=list)
    server_mods: List[str] = field(default_factory=list)
    cpu: int = 2
    debug: bool = False

    @classmethod
    def from_config_file(cls, config_file) -> List['DayzServerConfig']:
        configs = []
        with open(config_file,'r') as config:
            config_object = load(config, Loader=BaseLoader)
            for server in config_object['servers']:
                combined_config = config_object['shared'] | server
                configs.append(cls(**combined_config))
        return configs
    
@dataclass
class ServerData:
    online: bool
    ip: str
    port: int
    name: str
    map: str
    game: str
    description: str
    players: int
    max_players: int
    bots: int
    password_required: bool
    vac_secure: bool
    server_type: str
    os: str
    uptime: int



class DayzServer:

    def __init__(self, config):
        self.config = config
        self.process = None
        self.logger = getLogger(f'DayzServer[{self.config.server_name}]')
        self.start_time = -1

    def start_server(self):
        self.logger.info(f'Starting server')
        args = self._build_server_args()
        self.logger.debug(f'Base Path: {self.config.base_path}')
        self.logger.debug(f'Args: {args}')
        self.process = Popen(args)
        self.steamquery = SteamQuery("127.0.0.1",int(self.config.steamquery_port),timeout=5)
        self.start_time = time()
        self.logger.info(f'Server started with pid {self.process.pid}')

    def stop_server(self):
        self.logger.info("Stopping server")
        if not self.process:
            self.logger.debug("No server process to stop")
        elif not self.process.poll():
            self.logger.debug("Requesting server stop")
            self.process.terminate()
            try:
                self.process.wait(30)
            except TimeoutExpired:
                self.logger.debug("Server not stopping politely, killing")
                self.process.kill()
        else:
            self.logger.debug("Server process already dead")
        self.logger.info("Server stopped")
    
    def restart_server(self):
        self.stop_server()
        sleep(1)
        self.start_server()
        
    @property
    def is_alive(self) -> bool:
        if not self.process:
            return False
        if not self.process.poll():
            return True
        return False
    
    def get_server_data(self):
        if self.process and self.is_alive:
            data = self.steamquery.query_server_info()
            self.logger.debug(f'Server Data: {data}')
            if data and not data.get('error'):
                return ServerData(uptime=time() - self.start_time ,**data)
        return None

    def _build_server_args(self) -> List[str]:
        args = [
            self.config.executable, 
            f'-config={self.config.config_file}', 
            f'-port={self.config.port}', 
            f'"-profiles={self.config.profiles}"',
            f'-cpuCount={self.config.cpu}',
            f'-steamQueryPort={self.config.steamquery_port}'
            ]
        if self.config.mods:
            args.append(self._mods_to_commandline(self.config.mods, "mod"))
        if self.config.server_mods:
            args.append(self._mods_to_commandline(self.config.server_mods, "servermod"))
        for arg in self.config.extra_args:
            args.append(f'"-{arg}"')
        return args
    
    @staticmethod
    def _mods_to_commandline(mods: List[str], section: str) -> str:
        mod_command = '"-{section}='
        for mod in mods:
            mod_command += f'@{mod};'
        mod_command += '"'
        return mod_command

