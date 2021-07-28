#!/bin/python3

from cassandra.cluster import Cluster
from datetime import datetime, timedelta

API_CLUSTER = ['cassandra.xadi.io']
KEYSPACE = 'retrospect'
DAYS_TO_RETAIN = 7

CUTOFF = (datetime.now() - timedelta(days = DAYS_TO_RETAIN)).timestamp()

BATCH_STATEMENT = """\
BEGIN BATCH
{0}
APPLY BATCH;\
"""
# DELETE_STATEMENT = """
# DELETE FROM spans       WHERE session_id = '{0}';
# DELETE FROM events      WHERE session_id = '{0}';
# DELETE FROM snapshots   WHERE session_id = '{0}';
# """

DELETE_STATEMENT = """
DELETE FROM spans       WHERE session_id IN ('{0}');
DELETE FROM events      WHERE session_id IN ('{0}');
DELETE FROM snapshots   WHERE session_id IN ('{0}');
"""

def cleanse_spans(session):
    ids = {}
    rows = session.execute('SELECT session_id, time_sent FROM spans;')
    for row in rows:
        delta = (row.time_sent / 10**6)
        if CUTOFF > delta :
            ids[row.session_id] = True

    # commands = "".join([DELETE_STATEMENT.format(i) for i in ids])
    commands = DELETE_STATEMENT.format("', '".join(ids.keys()))
    batch = BATCH_STATEMENT.format(commands)

    # print(batch)
    session.execute(batch)

if __name__ == "__main__":
    cluster = Cluster(API_CLUSTER,port=9042)
    session = cluster.connect(KEYSPACE, wait_for_all_pools=True)
    session.execute(f'USE {KEYSPACE};')

    cleanse_spans(session)
