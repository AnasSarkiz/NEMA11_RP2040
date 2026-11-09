"""Export all unchanged native SVG sheets to a 300 dpi A4 review PDF.

Resvg preserves SVG transparent fills where the installed Inkscape converter did
not. Intermediate raster files stay in the ignored cache; native SVGs remain
available for vector review. This export does not approve schematic layout.
"""
import json
from pathlib import Path
import subprocess
import hashlib
from datetime import date
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape

manifest = json.loads(Path('checks/20261108-reconstruction/a4-sheet-export.json').read_text())
requirements = json.loads(Path('config/requirements.json').read_text())
page_count = requirements['schematic_sheet_count']
assert len(manifest['pages']) == page_count == 7, 'All seven source sheets are required'
assert hashlib.sha256(Path('dist/index/circuit.json').read_bytes()).hexdigest() == manifest['native_json_sha256'], 'Schematic manifest belongs to different native output'
cache = Path('.cache/20261108-reconstruction/a4-raster')
cache.mkdir(parents=True, exist_ok=True)
script = """
import {Resvg} from '@resvg/resvg-js';
import fs from 'node:fs';
const manifest = JSON.parse(fs.readFileSync('checks/20261108-reconstruction/a4-sheet-export.json'));
for (let i=0; i<manifest.pages.length; i++) {
  const renderer = new Resvg(fs.readFileSync(manifest.pages[i].file), {fitTo:{mode:'width',value:3508}});
  fs.writeFileSync('.cache/20261108-reconstruction/a4-raster/'+(i+1)+'.png',renderer.render().asPng());
}
"""
subprocess.run(['node','--input-type=module','-e',script],check=True,timeout=60)
output = Path('artifacts/20261108-reconstruction/NEMA11-schematics-A4-WIP.pdf')
width, height = landscape(A4)
pdf = canvas.Canvas(str(output),pagesize=(width,height),pageCompression=1)
pdf.setTitle('NEMA11 RP2040 — seven A4 schematic sheets — WIP')
for i, sheet in enumerate(manifest['pages'],1):
    pdf.drawImage(str(cache/f'{i}.png'),0,0,width=width,height=height)
    pdf.setFillColorRGB(.49,.12,.12)
    pdf.setFont('Helvetica',6)
    pdf.drawString(17,4,'WIP — schematic review only; unresolved validation issues; NOT fabrication-ready')
    pdf.drawRightString(width-17,4,f'{i}/{page_count} | {date.today().isoformat()}')
    pdf.showPage()
pdf.save()
reader=PdfReader(str(output))
assert len(reader.pages)==page_count
sizes=[[float(p.mediabox.width),float(p.mediabox.height)] for p in reader.pages]
assert all(abs(w-width)<.01 and abs(h-height)<.01 for w,h in sizes)
report={'pdf':str(output),'page_count':page_count,'page_size_points':sizes,'a4_landscape_verified':True,'vector_output':False,'raster_resolution_dpi':300,'raster_width_pixels':3508,'renderer':'@resvg/resvg-js + ReportLab','native_svg_unchanged':True,'vector_svg_files':[p['file'] for p in manifest['pages']],'components_covered':manifest['components_covered'],'schematic_ports_covered':manifest['schematic_ports_covered'],'native_json_sha256':manifest['native_json_sha256'],'historical_20261023_conversion_observations':['Installed Inkscape rendered transparent shapes as black fills; that PDF was rejected.','Installed headless Chromium timed out after 60 seconds; not attributed to tscircuit.'],'layout_approved':False,'manufacturing_approved':False}
Path('checks/20261108-reconstruction/a4-pdf-export.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
