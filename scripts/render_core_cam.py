#!/usr/bin/env python3
"""Render the original review copper files with the independent PyGerber parser."""
import hashlib,json
from pathlib import Path
from pygerber.gerberx3.api import v2

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/rp2040-pcb'
files=[]
for name,layer in [('F_Cu','top'),('In1_Cu','inner1'),('In2_Cu','inner2'),('B_Cu','bottom')]:
    source=OUT/'review-cam'/f'{name}.gbr'
    target=OUT/f'independent-cam-{layer}.png'
    v2.GerberFile.from_file(source).parse(on_parser_error=v2.OnParserErrorEnum.Raise).render_raster(
        target,dpmm=40,color_scheme=v2.ColorScheme.COPPER)
    files.append({'layer':layer,'source':str(source.relative_to(ROOT)),
                  'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                  'render':str(target.relative_to(ROOT)),
                  'render_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(OUT/'independent-cam-render.json').write_text(json.dumps({'parser':'PyGerber 2.4.3',
    'original_CAM_bytes_rendered':True,'pixels_per_mm':40,'files':files,
    'render_scope':'Four individual copper layers before drill subtraction; not a complete assembly rendering',
    'manufacturing_release':False},indent=2)+'\n')
print('Rendered all four original copper Gerbers with independent PyGerber.')
