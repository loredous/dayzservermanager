from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, fields
from sys import argv
from typing import Dict, List
from dayz_servermanager.server import DayzServer, DayzServerConfig, ServerData
from logging import getLogger, basicConfig, DEBUG, INFO
from time import time, sleep
from yaml import load, BaseLoader
from os import system, name

def parse_args(args) -> Namespace:
    parser = ArgumentParser(prog='DayZ Server Manager')
    parser.add_argument('-c','--config',help='Location of the server manager config file',default='config.yaml')
    parser.add_argument('-v','--verbose',help='Enable verbose logging', action='store_true')
    return parser.parse_args(args[1:])

@dataclass
class DayzRunningServer:
    pid: int
    start_time: float
    server: DayzServer

@dataclass
class ServerManagerConfig:
    startup_delay: int = 60
    update_interval: int = 30
    continue_on_steamquery: bool = False

    def __post_init__(self):
        for field in fields(self):
            setattr(self, field.name, field.type(getattr(self, field.name)))

    @classmethod
    def from_config_file(cls, config_file) -> 'ServerManagerConfig':
        with open(config_file, 'r') as config:
            config_object = load(config, Loader=BaseLoader)
            return cls(**config_object.get('app_config', {}))

class ServerManager:
    def __init__(self, server_configs: List[DayzServerConfig], manager_config: ServerManagerConfig):
        self.logger = getLogger("ServerManager")
        self.servers = {}
        self.logger.info(f'Loading configs for {len(server_configs)} servers')
        self.last_server_start = -1
        self.config = manager_config
        for config in server_configs:
            self.servers[config.server_name] = DayzRunningServer(-1, -1, DayzServer(config))

    def start_server(self, server_name: str):
        if time() - self.last_server_start < self.config.startup_delay:
            self.logger.info(f'Not starting server {server_name}. In backoff period')
            return
        server = self.servers.get(server_name)
        if server:
            server.server.start_server()
            server.pid = server.server.process.pid
            server.start_time = time()
            self.last_server_start = time()
            self.starting_server = server
        else:
            self.logger.error(f'No server with name {server_name}')

    def restart_server(self, server_name: str):
        if time() - self.last_server_start < self.config.startup_delay:
            self.logger.info(f'Not restarting server {server_name}. In backoff period')
            return
        server = self.servers.get(server_name)
        if server:
            server.server.stop_server()
            self.start_server(server_name)
        else:
            self.logger.error(f'No server with name {server_name}')

    def run(self):
        try:
            self.starting_server = None
            while True:
                clear_console()
                print('========== DayZ Server Manager ==========')
                for server in self.servers.values():
                    self.print_server_report(server.server.config.server_name)
                print('=========================================')
                if self.starting_server and self.config.continue_on_steamquery:
                    if server_data := self.starting_server.server.get_server_data():
                        if server_data.online:
                            self.logger.info(f'Server {self.starting_server.server.config.server_name} shows online via SteamQuery. Skipping backoff period')
                            self.starting_server = None
                            self.last_server_start = -1
                for server in self.servers.values():
                    self.logger.debug(f'Server {server.server.config.server_name}, process: {server.server.process}, Alive: {server.server.is_alive}')
                    if not server.server.process or not server.server.is_alive:
                        self.logger.debug(f'Server {server.server.config.server_name} is dead, trying to start')
                        self.start_server(server.server.config.server_name)
                    else:
                        self.logger.debug(f'Server {server.server.config.server_name} is alive for {time() - server.start_time} seconds')
                        if time() - server.start_time > int(server.server.config.restart_time)*60:
                            self.logger.info(f'Server {server.server.config.server_name} is alive for {time() - server.start_time} seconds, restarting')
                            self.restart_server(server.server.config.server_name)
                sleep(self.config.update_interval)
        except KeyboardInterrupt:
            self.logger.info('Got Ctrl+C. Shutting down!')
            for server in self.servers.values():
                self.logger.info(f'Stopping server {server.server.config.server_name}')
                server.server.stop_server()

    def print_server_report(self, server_name):
        server = self.servers.get(server_name)
        if server:
            data: ServerData = server.server.get_server_data()
            if data:
                print(f'Server: {server_name} ({data.ip}:{data.port}) | {data.players}/{data.max_players} | Uptime: {int(data.uptime/60)}')
            else:
                print(f'No data for server {server_name}')
        else:
            print(f'No server with name {server_name}')
        

def clear_console():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def main():
    arguments = parse_args(argv)
    basicConfig(level=DEBUG if arguments.verbose else INFO)
    logger = getLogger()
    logger.info('Starting DayZ Server Manager')
    server_configs = DayzServerConfig.from_config_file(arguments.config)
    manager_config = ServerManagerConfig.from_config_file(arguments.config)
    logger.info(f'Got configs for {len(server_configs)} servers')
    manager = ServerManager(server_configs, manager_config)
    manager.run()

if __name__ == '__main__':
    main()