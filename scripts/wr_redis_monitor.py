'''
Simple script to poll WR-LEN endpoints by hostname and
write stats to redis and also dynamic stats to JSON file
'''

def main():
    import socket
    import argparse
    import redis
    import time
    import datetime
    import os
    import json
    from wr_cm.wr_len import WrLen
    from wr_cm import __version__

    # JSON filename - WR-LEN dynamic stats are written to this file
    json_filename = "dynamic_wrlen_stats.json"

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
                    wr_devices[host] = WrLen(host)
                except:
                    print("Error while connecting to %s" % host)
                    continue
            print("%d: polling %s" % (count, host))
            try:
                stats = wr_devices[host].gather_keys(include_ver=False)
                
                #print("wr0_rx = ", stats['wr0_rx'])
                #print(json.dumps(stats['temp']))
                
                # Create dictionary of dynamic stats from WR-LENs and convert to JSON
                dynamic_stats = {"temp":stats['temp'].encode('ascii'),
                "timestamp":stats['timestamp'].encode('ascii'),
                "wr0_rx":stats['wr0_rx'],
                "wr0_tx":stats['wr0_tx'],
                "wr1_rx":stats['wr1_rx'],
                "wr1_tx":stats['wr1_tx'],
                "wr0_lnk":stats['wr0_lnk'],
                "wr1_lnk":stats['wr1_lnk'],
                "wr0_setp":stats['wr0_setp'],
                "wr0_cko":stats['wr0_cko'],
                "wr0_mu":stats['wr0_mu'],
                "wr0_crtt":stats['wr0_crtt'],
                "wr0_ucnt":stats['wr0_ucnt'],
                "mode":stats['mode'].encode('ascii'),
                "wr0_ss":stats['wr0_ss'].encode('ascii')}
                
                # Convert to JSON
                dynamic_stats_json = json.dumps(dynamic_stats)
                print(dynamic_stats_json)
                
                # Write dictionary to JSON file
                with open(json_filename, "w") as outfile:
                    #outfile.write(dynamic_stats_json) # The strings in the dictionary are written as unicode strings
                    json.dump(dynamic_stats_json, outfile)
                    
                # Read JSON file. 
                with open(json_filename, "r") as outfile:
                    read_json_file = json.load(outfile)
                    
                print("JSON file output")
                print(read_json_file)
                
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
