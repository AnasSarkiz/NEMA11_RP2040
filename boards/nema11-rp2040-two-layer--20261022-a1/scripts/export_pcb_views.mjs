// Native, layer-specific review views. These are not routed or fabrication views.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {convertCircuitJsonToPcbSvg} from 'circuit-to-svg';
import {Resvg} from '@resvg/resvg-js';

const input = 'dist/index/circuit.json';
const raw = fs.readFileSync(input);
const circuit = JSON.parse(raw);
const output = 'artifacts/20261108-reconstruction/pcb';
fs.mkdirSync(output, {recursive:true});
const views = [];
for (const layer of ['top', 'bottom']) {
  const options = {layer, width:1600, height:1600, shouldDrawErrors:true,
    shouldDrawWarnings:true, showErrorsInTextOverlay:true, showCourtyards:true,
    drawPaddingOutsideBoard:true, includeVersion:true};
  const svg = convertCircuitJsonToPcbSvg(circuit, options);
  const svgPath = path.join(output, `${layer}.svg`);
  const pngPath = path.join(output, `${layer}.png`);
  fs.writeFileSync(svgPath, svg);
  fs.writeFileSync(pngPath, new Resvg(svg).render().asPng());
  views.push({layer, options, svg:svgPath, png:pngPath});
}
const manifest = {native_json:input,
  native_json_sha256:crypto.createHash('sha256').update(raw).digest('hex'),
  renderer:'circuit-to-svg official convertCircuitJsonToPcbSvg, rasterized by @resvg/resvg-js',
  views, scope:'Layer-specific 2D review only; native errors and warnings enabled. Does not establish plug, bolt, motor, height, electrical routing or assembly clearance.',
  manufacturing_approved:false, layout_approved:false};
fs.writeFileSync('checks/20261108-reconstruction/pcb-view-export.json', JSON.stringify(manifest,null,2)+'\n');
console.log('Exported native top and bottom PCB review views with diagnostics enabled');
