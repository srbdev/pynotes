import os
import argparse
import sqlite3
from datetime import datetime
from os.path import expanduser

import editor


DATABASE = expanduser("~") + "/.pynotes.db"

parser = argparse.ArgumentParser(description="Write and manage notes from the command line.")
parser.add_argument("--init", help="initialize pynotes for the user", action="store_true")
parser.add_argument("-c", "--create", help="create a new topic", metavar="topic")
parser.add_argument("-t", "--topics", help="list all available topics", action="store_true")
parser.add_argument("-a", "--add", help="add a note to a topic", metavar="topic")
parser.add_argument("-l", "--list", help="list notes from a topic", metavar="topic")
parser.add_argument("-e", "--edit", help="edit a note from a topic", nargs=2, metavar=("id", "topic"))
parser.add_argument("-d", "--delete", help="delete a note from a topic", nargs=2, metavar=("id", "topic"))
parser.add_argument("--delete-topic", help="delete a topic", metavar="name")

def get_connection():
    if os.path.isfile(DATABASE):
        return sqlite3.connect(DATABASE)
    else:
        print("No database present! Use the --init option to create one.")
        sys.exit()

def runsql(query, tuple=None):
    conn = get_connection()

    if tuple is not None:
        conn.execute(query, tuple)
    else:
        conn.execute(query)
    conn.commit()
    conn.close()

def is_table(name):
    try:
        runsql("SELECT * FROM %s" % name)
        return True
    except:
        print("Topic %s does not exist" % name)
        return False

def fetchall(query, tuple=None):
    conn = get_connection()
    cur = conn.cursor()

    if tuple is not None:
        cur.execute(query, tuple)
    else:
        cur.execute(query)

    return cur.fetchall()

def fetchone(query, tuple=None):
    conn = get_connection()
    cur = conn.cursor()

    if tuple is not None:
        cur.execute(query, tuple)
    else:
        cur.execute(query)

    return cur.fetchone()

def init():
    try:
        sqlite3.connect(DATABASE)
    except Exception:
        print("Error while creating the database. Please check your permissions!")
        sys.exit()

def create_topic(name):
    sql = """CREATE TABLE %s(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, note TEXT, created_at TIMESTAMP, modified_at TIMESTAMP)""" % name.strip()
    runsql(sql)

def add_note(name):
    if not is_table(name):
        print("Aborted!")
        return

    note = editor.open('i')
    note = note.decode("utf-8") # convert from bytes to string
    timestamp = datetime.utcnow()
    runsql("INSERT INTO %s (note, created_at, modified_at) VALUES (?, ?, ?)" % name, (note, timestamp, timestamp))

def list_notes(topic):
    if not is_table(topic):
        print("Aborted!")
        return

    sql = "SELECT * FROM %s" % topic
    rows = fetchall(sql)
    str_length = 25

    for row in rows:
        snippet = (row[1][:str_length] + "...").encode("utf-8") if len(row[1]) > str_length+3 else row[1].encode("utf-8")
        snippet = snippet.decode("utf-8").replace("\n", " ")
        snippet = snippet.replace("b'", "")
        snippet = snippet.replace("'", "")

        print("(%s) %s - last modified: %s" % (row[0], snippet, row[3]))

def delete_note(args):
    if not is_table(args[1]):
        print("Aborted!")
        return

    a = input("Are you sure you want to delete note with ID %s from %s? " % (args[0], args[1]))

    if a == "y" or a == "Y" or a == "yes" or a == "YES":
        sql = "DELETE FROM %s WHERE id = %s" % (args[1], args[0])
        runsql(sql)
    else:
        print("Aborted!")

def delete_topic(arg):
    if not is_table(arg):
        print("Aborted!")
        return

    a = input("Are you sure you want to delete topic %s? " % arg)

    if a == "y" or a == "Y" or a == "yes" or a == "YES":
        sql = "DROP TABLE %s" % arg
        runsql(sql)
    else:
        print("Aborted")

def edit_note(args):
    if not is_table(args[1]):
        print("Aborted!")
        return

    sql = "SELECT note FROM %s WHERE id = %s" % (args[1], args[0])
    note = fetchone(sql)

    new_note = editor.open(None, note[0].encode("utf-8"))
    new_note = new_note.decode("utf-8") # convert from bytes to string
    modified_at = datetime.utcnow()
    runsql("UPDATE %s SET note=?, modified_at=? WHERE id=?" % args[1], (new_note, modified_at, args[0]))

def list_topics():
    sql = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = fetchall(sql)

    for table in tables:
        if ("%s" % table) != "sqlite_sequence":
            print("%s" % table)


args = parser.parse_args()

if args.add is not None:                add_note(args.add)
elif args.create is not None:           create_topic(args.create)
elif args.list is not None:             list_notes(args.list)
elif args.delete is not None:           delete_note(args.delete)
elif args.delete_topic is not None:     delete_topic(args.delete_topic)
elif args.edit is not None:             edit_note(args.edit)
elif args.topics is True:               list_topics()
elif args.init is True:                 init()
else:                                   print(parser.print_help())
