import os
import sys, tempfile
from subprocess import call


EDITOR = os.environ.get("EDITOR", "vim")

def open(mode=None, content=None):
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        if content is not None:
            tf.write(content)
            tf.flush()

        if mode is None:
            call([EDITOR, tf.name])
        elif mode == 'i':
            call([EDITOR, "+star", tf.name])

        tf.seek(0)
        return tf.read()
