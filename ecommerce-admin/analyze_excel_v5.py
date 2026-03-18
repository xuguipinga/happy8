import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import io

file_path = r'd:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\excel-model\克罗心最新表格.xlsx'

def analyze_drawings():
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            # 1. Read sheet1 rels to find drawing
            sheet_rels_path = 'xl/worksheets/_rels/sheet1.xml.rels'
            if sheet_rels_path in z.namelist():
                print(f"Reading {sheet_rels_path}...")
                root = ET.fromstring(z.read(sheet_rels_path))
                drawing_id = None
                for rel in root:
                    if 'drawing' in rel.attrib.get('Type', ''):
                        drawing_id = rel.attrib.get('Target')
                        break
                
                if drawing_id:
                    # drawing_id is like '../drawings/drawing1.xml'
                    dp = drawing_id.replace('../drawings/', 'xl/drawings/')
                    print(f"Found drawing path: {dp}")
                    
                    # 2. Read drawing1.xml
                    if dp in z.namelist():
                        draw_root = ET.fromstring(z.read(dp))
                        # Namespaces
                        ns = {
                            'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                        }
                        
                        # 3. Read drawing rels to map rId to file
                        rel_path = f'xl/drawings/_rels/{os.path.basename(dp)}.rels'
                        rel_map = {}
                        if rel_path in z.namelist():
                            rel_root = ET.fromstring(z.read(rel_path))
                            for r in rel_root:
                                rel_map[r.attrib.get('Id')] = r.attrib.get('Target').replace('../media/', 'xl/media/')
                        
                        # 4. Find anchors
                        print("\nAnchors found in XML:")
                        for anchor in draw_root.findall('.//xdr:twoCellAnchor', ns):
                            from_row = anchor.find('.//xdr:from/xdr:row', ns).text
                            from_col = anchor.find('.//xdr:from/xdr:col', ns).text
                            pic = anchor.find('.//xdr:pic/xdr:blipFill/a:blip', ns)
                            if pic is not None:
                                rId = pic.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                                img_file = rel_map.get(rId)
                                print(f"  Row: {from_row}, Col: {from_col} -> {img_file}")
            else:
                print("No sheet1 rels found.")
    except Exception as e:
        print(f"Error: {e}")

import os
analyze_drawings()
