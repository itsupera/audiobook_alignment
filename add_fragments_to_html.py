"""
Add fragments f0001, f0002, ... to each p tag, needed for afaligner to work.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = "{http://www.w3.org/1999/xhtml}"


def main():
    inputfile = "samples/sample1_no_fragments.html"
    tree = ET.parse(inputfile)
    ps = tree.findall(f'.//{NAMESPACE}p')
    for idx, p in enumerate(ps):
        p.set("id", f"f{str(idx).zfill(5)}")

    outputfile = "afaligner_data/text/sample1.xhtml"
    Path(outputfile).parent.mkdir(exist_ok=True, parents=True)
    tree.write(outputfile, encoding="UTF-8", xml_declaration=True)

if __name__ == '__main__':
    main()