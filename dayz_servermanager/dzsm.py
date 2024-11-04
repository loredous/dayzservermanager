from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from sys import argv
from typing import Dict, List
from dayz_servermanager.models import DayzServer, DayzServerConfig
from logging import getLogger, basicConfig, DEBUG, INFO
from time import time, sleep

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

class ServerManager:

    def __init__(self, configs: List[DayzServerConfig], startup_delay: int = 60):
        self.logger = getLogger("ServerManager")
        self.servers = {}
        self.logger.info(f'Loading configs for {len(configs)} servers')
        self.startup_delay = startup_delay
        self.last_server_start = -1
        for config in configs:
            self.servers[config.server_name] = DayzRunningServer(-1, -1, DayzServer(config))

    def start_server(self, server_name: str):
        if time() - self.last_server_start < self.startup_delay:
            self.logger.info(f'Not starting server {server_name}. In backoff period')
            return
        server = self.servers.get(server_name)
        if server:
            server.server.start_server()
            server.pid = server.server.process.pid
            server.start_time = time()
        else:
            self.logger.error(f'No server with name {server_name}')

    def restart_server(self, server_name: str):
        if time() - self.last_server_start < self.startup_delay:
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
            while True:
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
                sleep(30)
        except KeyboardInterrupt:
            self.logger.info('Got Ctrl+C. Shutting down!')
            for server in self.servers.values():
                self.logger.info(f'Stopping server {server.server.config.server_name}')
                server.server.stop_server()


def main():
    arguments = parse_args(argv)
    basicConfig(level=DEBUG if arguments.verbose else INFO)
    logger = getLogger()
    logger.info('Starting DayZ Server Manager')
    configs = DayzServerConfig.from_config_file(arguments.config)
    logger.info(f'Got configs for {len(configs)} servers')
    manager = ServerManager(configs)
    manager.run()

if __name__ == '__main__':
    main()