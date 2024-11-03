from argparse import ArgumentParser, Namespace
from sys import argv
from typing import Dict, List
from models import DayzServer, DayzServerConfig
from logging import getLogger, basicConfig, DEBUG, INFO
from time import time, sleep

def parse_args(args) -> Namespace:
    parser = ArgumentParser(prog='DayZ Server Manager')
    parser.add_argument('-c','--config',help='Location of the server manager config file',default='config.yaml')
    parser.add_argument('-v','--verbose',help='Enable verbose logging', action='store_true')
    return parser.parse_args()

class ServerManager:
    servers: Dict[str,DayzServer]

    def __init__(self, configs: List[DayzServerConfig]):
        self.logger = getLogger("ServerManager")
        self.servers = {}
        self.logger.info(f'Loading configs for {len(configs)} servers')
        for config in configs:
            self.servers[config.server_name] = DayzServer(config)


    def run(self):
        last_server_start = None
        try:
            while True:
                for server in self.servers.values():
                    if not server.process or not server.is_alive:
                        self.logger.debug(f'Server {server.config.server_name} is dead, trying to start')
                        server.start_server()
                sleep(30)
        except KeyboardInterrupt:
            self.logger.info('Got Ctrl+C. Shutting down!')


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