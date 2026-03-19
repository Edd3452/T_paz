import pandas as pd
import os

from app import shapefile_mapping

df = pd.read_csv('https://docs.google.com/spreadsheets/d/1RdV79i1ifRCt_r3j8zEDqt71ItqNRO39MpB1fKA8uZY/export?format=csv&gid=0')
failed = []
missed_files = []

for _, row in df.iterrows():
    name = str(row['Territorio de paz']).strip()
    shp_file = shapefile_mapping.get(name)
    if not shp_file:
        failed.append(name)
    elif not os.path.exists(shp_file):
        missed_files.append((name, shp_file))

print('Failed keys:', failed)
print('Missing files:', missed_files)
