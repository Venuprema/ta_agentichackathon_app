import zipfile
import xml.etree.ElementTree as ET
import os
os.chdir(r"d:\AI Experiments\Projects\Agentic Hackathon AI")
z = zipfile.ZipFile("AI Agents Hackathon @ Wendy's (1).pptx", 'r')
for name in sorted(z.namelist()):
    if 'slide' in name and name.endswith('.xml') and 'slideLayout' not in name and 'slideMaster' not in name:
        data = z.read(name)
        root = ET.fromstring(data)
        for t in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
            if t.text:
                print(t.text)
        print('---SLIDE---')
z.close()
