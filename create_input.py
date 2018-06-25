import argparse
import logging
from pymongo import MongoClient

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Create input file for tensorflow')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=27017)
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--logfile')
    parser.add_argument('--loglevel', type=str, default='debug')
    parser.add_argument('--newspaper')

    # parse arguments
    args = parser.parse_args()

    if args.loglevel == 'info':
        lvl = logging.INFO
    elif args.loglevel == 'debug':
        lvl = logging.DEBUG
    else:
        lvl = logging.DEBUG
    logging.basicConfig(level=lvl, filename=args.logfile, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    client = MongoClient(args.host, args.port, username=args.username, password=args.password)
    db = client.forumdata
    filter = {}
    if args.newspaper:
        filter['newspaper'] = args.newspaper

    with open("input.txt", "w") as f:

        for p in db.postings.find(filter):
            t = p.get('text') + '\n'
            f.write(t.encode('utf8'))



