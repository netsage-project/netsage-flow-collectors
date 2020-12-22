#!/usr/bin/env python3
from loguru import logger
import argparse
from gen_lib.config import load_config
from gen_lib.process import Process
import gen_lib
import gila


def parse_args():
    parser = argparse.ArgumentParser(
        description='Netsage Flow generator')
    parser.add_argument('--config', dest='config',
                        default='./gen_config/collectors.yaml', help='Override config file')
    parser.add_argument('--debug', dest='debug',
                        action='store_true', default=False, help='Debug mode')
    parser.add_argument('--remote', dest='remote', action='store_true',
                        default=False, help='Enables Remote mode')
    parser.add_argument('--clean', dest='clean', action='store_true', default=False,
                        help='Cleanup all generated configs')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.remote:
        logger.debug("Starting Debug Mode")
        try:
            import debugpy

            # Allow other computers to attach to debugpy at this IP address and port.
            debugpy.listen(('0.0.0.0', 8000))
            # Pause the program until a remote debugger is attached
            debugpy.wait_for_client()
        except Exception as exc:
            logger.error(exc)
    load_config(args.config, args.debug)
    p = Process()
    p.run()


if __name__ == '__main__':
    main()
