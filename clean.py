import os
import sys
import re

OUTPUT_ROOT = "penguinz1.github.io"

if (len(sys.argv) >= 2):
    OUTPUT_ROOT = sys.argv[1]

files = os.listdir(OUTPUT_ROOT)
for file in files:
    if (re.search(".html", file)):
        os.remove(f'{OUTPUT_ROOT}/{file}')

files = os.listdir(f'{OUTPUT_ROOT}/static')
for file in files:
    os.remove(f'{OUTPUT_ROOT}/static/{file}')