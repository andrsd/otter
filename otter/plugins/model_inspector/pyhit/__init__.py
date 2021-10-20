# flake8: noqa
import os
import sys
import subprocess

try:
    import hit

except ImportError:
    hit_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'hit')
    sys.path.append(hit_dir)
    try:
        import hit
    except ImportError:
        subprocess.run(['make', 'hit.so'], cwd=hit_dir)
        import hit
