import argparse
import sys, tempfile
from subprocess import call
import sqlite3
from datetime import datetime
import os

DATABASE = "notes.db"
EDITOR = os.environ.get("EDITOR", "vim")

parser = argparse.ArgumentParser(description="Write and manage notes from the command line.")
parser.add_argument("-c", "--create", help="create a new topic", metavar="topic")
parser.add_argument("-a", "--add", help="add a note to a topic", metavar="topic")

def get_connection():
    return sqlite3.connect(DATABASE)

def run_query(query, tuple=None):
    conn = get_connection()

    if tuple is not None:
        conn.execute(query, tuple)
    else:
        conn.execute(query)
    conn.commit()
    conn.close()

def create_topic(name):
    sql = """CREATE TABLE %s(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, note TEXT, created_at TIMESTAMP, modified_at TIMESTAMP)""" % name.strip()
    run_query(sql)

def add_note(name):
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        call([EDITOR, tf.name])
        tf.seek(0)
        note = tf.read()
        timestamp = datetime.utcnow()

        run_query("INSERT INTO %s (note, created_at, modified_at) VALUES (?, ?, ?)" % name, (note, timestamp, timestamp))

args = parser.parse_args()

if args.add is not None:
    add_note(args.add)
elif args.create is not None:
    create_topic(args.create)
else:
    print parser.print_help()
