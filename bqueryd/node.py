#!/srv/python/venv/bin/ipython -i
import bqueryd
import os
import sys
import logging
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(['/etc/bqueryd.cfg', os.path.expanduser('~/.bqueryd.cfg')])

redis_url=config.get('Main', 'redis_url')

if __name__ == '__main__':
    if '-v' in sys.argv:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    if 'controller' in sys.argv:
        bqueryd.ControllerNode(redis_url=redis_url, loglevel=loglevel).go()
    elif 'worker' in sys.argv:
        bqueryd.WorkerNode(redis_url=redis_url, loglevel=loglevel).go()
    else:
        if len(sys.argv) > 1 and sys.argv[1].startswith('tcp:'):
            rpc = bqueryd.RPC(address=sys.argv[1], redis_url=redis_url, loglevel=loglevel)
        else:
            rpc = bqueryd.RPC(redis_url=redis_url, loglevel=loglevel)
        sys.stderr.write('Run this script with python -i , and then you will have a variable named "rpc" as a connection.\n')
