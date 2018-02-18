import argparse
import sys, tempfile
from subprocess import call

parser = argparse.ArgumentParser(description="Write and manage notes from the command line.")
parser.add_argument("-c", "--create", help="create a new topic", metavar="topic")
parser.add_argument("-a", "--add", help="add a note to a topic", metavar="topic")

def create_topic(name):
    print name

def add_note(name):
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        call(["vim", tf.name])

        tf.seek(0)
        note = tf.read()


args = parser.parse_args()

if args.add is not None:
    add_note(args.add)
elif args.create is not None:
    create_topic(args.create)
else:
    print parser.print_help()
