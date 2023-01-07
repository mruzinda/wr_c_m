'''
Simple script to poll WR-LEN endpoints by hostname and
write stats to redis
'''

def main():
    import socket
    import argparse
    import redis
    import time
    import datetime
    import os
    from wr_cm.wr_len import WrLen
    from wr_cm import __version__

    hostname = socket.gethostname()

    parser = argparse.ArgumentParser(description='VUART shell for WR-LEN')
    parser.add_argument('hosts', metavar='hosts', type=str, nargs='*',
                    help='WR hosts to poll. Default: Node{0..32}wr')
    parser.add_argument('-t', dest='polltime', type=float, default=30,
                    help='Minimum time between polling cycles in seconds. Default: 30s')
#    r = redis.Redis('redishost')
    r = redis.Redis()

    args = parser.parse_args()
    
    if len(args.hosts) == 0:
        hosts = ['Node%dwr' % x for x in range(32)]
    else:
        hosts = args.hosts

    print('Begging WR-LEN status polling. Hosts are:')
    print(hosts)
    script_redis_key = "status:script:%s:%s" % (hostname, __file__)
    wr_devices = {}
    count = 0
    while(True):
        r.set(script_redis_key, "alive", ex=60)
        r.hmset("version:%s:%s" % (__package__, os.path.basename(__file__)), {"version":__version__, "timestamp":datetime.datetime.now().isoformat()})
        start_time = time.time()
        count += 1
        for host in hosts:
            hash_key = 'status:wr:%s' % host
            if host not in wr_devices.keys():
                try:
                    ip = socket.gethostbyname(host)
                except socket.gaierror:
                    continue
                try:
                    print(host)
                    wr_devices[host] = WrLen(host)
                except:
                    print("Error while connecting to %s" % host)
                    continue
            print("%d: polling %s" % (count, host))
            try:
                stats = wr_devices[host].gather_keys(include_ver=False)
                r.hmset(hash_key, stats)
                # Delete old keys in case there is some weird stale stuff
                old_keys = [k for k in r.hkeys(hash_key) if k not in stats.keys()]
                if len(old_keys) > 0:
                    r.hdel(hash_key, *old_keys)
            except:
                print("Error while polling %s" % host)
        extra_wait = args.polltime - (time.time() - start_time)
        while extra_wait > 0:
            r.set(script_redis_key, "alive", ex=60)
            time.sleep(min(extra_wait, 60))
            extra_wait -= 60

if __name__ == '__main__':
    main()
