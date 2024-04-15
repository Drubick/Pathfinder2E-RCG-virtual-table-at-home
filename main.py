
import sys
import os
sys.path.append('/mnt/c/Users/Valentin/Desktop/DATABASE RGE DEFINITIVO/Dungeon-crawler')
os.path.abspath('/mnt/c/Users/Valentin/Desktop/DATABASE RGE DEFINITIVO/Dungeon-crawler')
import combat_generator.RCG_logic as Generator

generator = Generator

generator.generate(4,2,"Low")