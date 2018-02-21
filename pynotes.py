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
parser.add_argument("-l", "--list", help="list notes from a topic", metavar="topic")

def run_editor():
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        call([EDITOR, tf.name])
        tf.seek(0)
        return tf.read()

def get_connection():
    return sqlite3.connect(DATABASE)

def runsql(query, tuple=None):
    conn = get_connection()

    if tuple is not None:
        conn.execute(query, tuple)
    else:
        conn.execute(query)
    conn.commit()
    conn.close()

def fetchall(query, tuple=None):
    conn = get_connection()
    cur = conn.cursor()

    if tuple is not None:
        cur.execute(query, tuple)
    else:
        cur.execute(query)

    return cur.fetchall()

def create_topic(name):
    sql = """CREATE TABLE %s(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, note TEXT, created_at TIMESTAMP, modified_at TIMESTAMP)""" % name.strip()
    runsql(sql)

def add_note(name):
    note = run_editor()
    timestamp = datetime.utcnow()
    runsql("INSERT INTO %s (note, created_at, modified_at) VALUES (?, ?, ?)" % name, (note, timestamp, timestamp))

def list_notes(topic):
    sql = """SELECT * FROM %s""" % topic
    rows = fetchall(sql)
    str_length = 25

    for row in rows:
        print "(%s) %s - last modified: %s" % (row[0], (row[1][:str_length] + "...").encode('unicode_escape') if len(row[1]) > str_length+3 else row[1].encode('unicode_escape'), row[3])


args = parser.parse_args()

if args.add is not None:
    add_note(args.add)
elif args.create is not None:
    create_topic(args.create)
elif args.list is not None:
    list_notes(args.list)
else:
    print parser.print_help()
