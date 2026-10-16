#!/usr/bin/env python3
"""Run native CLI login without displaying its token-bearing npmrc fallback.

Only the official browser authorization URL and fixed status messages may reach
stdout. Credentials remain in the CLI's private configuration outside Git.
"""
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse


def main():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.update(XDG_CONFIG_HOME='/workspace/.config',
               XDG_CACHE_HOME='/workspace/.cache',
               XDG_DATA_HOME='/workspace/.local/share')
    env['PATH'] = str(root / 'tools/pcb/node_modules/.bin') + ':' + env['PATH']
    process = subprocess.Popen(['tsci', 'auth', 'login'], cwd=root, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1)
    issued = False
    denied = False
    try:
        for line in process.stdout:
            text = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
            if text.startswith('https://') and urlparse(text).hostname in (
                    'tscircuit.com', 'www.tscircuit.com'):
                print('CLI authorization URL: ' + text, flush=True)
                issued = True
            elif ('403' in text or 'Forbidden' in text) and not denied:
                print('CLI login blocked: HTTP 403. Check environment network access.', flush=True)
                denied = True
            elif text == 'Ready to use!':
                print('CLI login completed. Credentials were not displayed.', flush=True)
            elif text.startswith('Already logged in as '):
                print('CLI already has a login. Verify account access before publication.', flush=True)
            # The CLI may print a raw token when its global npmrc is read-only.
            # Suppress every other line; do not save unfiltered output to disk.
        code = process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        return 130
    if code and not issued:
        print('No CLI authorization link was issued.', flush=True)
    if code:
        print('CLI login failed with exit code ' + str(code), flush=True)
    return code


if __name__ == '__main__':
    sys.exit(main())
