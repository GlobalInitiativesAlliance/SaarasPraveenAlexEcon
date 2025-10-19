#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
except ImportError:
    print('Installing pygame...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame==2.5.2'])
    import pygame

print('Starting Economics Adventure Game...')
from src.main import main
import asyncio
asyncio.run(main())
