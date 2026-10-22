// Read native circuit JSON and render each sheet through the official API.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {convertCircuitJsonToSchematicSvg} from 'circuit-to-svg';
const input = 'dist/index/circuit.json';
const output = 'artifacts/20261023/schematic';
const native = fs.readFileSync(input);
const circuit = JSON.parse(native);
const sheets = circuit.filter(e => e.type === 'schematic_sheet').sort((a,b) => a.sheet_index-b.sheet_index);
if (sheets.length !== 6 || sheets.some(s => s.sheet_size !== 'a4')) throw new Error('Expected all six native A4 sheets');
const names = new Map(circuit.filter(e => e.type === 'source_component').map(e => [e.source_component_id,e.name]));
const covered = new Set();
fs.mkdirSync(output,{recursive:true});
const pages = [];
for (const sheet of sheets) {
  const filename = `${String(sheet.sheet_index+1).padStart(2,'0')}.svg`;
  const svg = convertCircuitJsonToSchematicSvg(circuit,{schematicSheetId:sheet.schematic_sheet_id,width:1188,height:840});
  fs.writeFileSync(path.join(output,filename),svg);
  const components=circuit.filter(e => e.type==='schematic_component' && e.schematic_sheet_id===sheet.schematic_sheet_id);
  const ports=circuit.filter(e => e.type==='schematic_port' && e.schematic_sheet_id===sheet.schematic_sheet_id);
  for (const component of components) {
    if(covered.has(component.source_component_id)) throw new Error('A component appears on multiple sheets');
    covered.add(component.source_component_id);
  }
  pages.push({sheet_id:sheet.schematic_sheet_id,name:sheet.name,file:path.join(output,filename),component_names:components.map(e=>names.get(e.source_component_id)),component_count:components.length,port_count:ports.length,native_connected_port_count:ports.filter(e=>e.is_connected).length});
}
const total = circuit.filter(e=>e.type==='schematic_component').length;
if(covered.size!==total) throw new Error('Not all native schematic components were exported');
const manifest={native_json:input,native_json_sha256:crypto.createHash('sha256').update(native).digest('hex'),renderer:'circuit-to-svg official convertCircuitJsonToSchematicSvg with schematicSheetId',pages,components_covered:covered.size,schematic_ports_covered:pages.reduce((n,p)=>n+p.port_count,0),manufacturing_approved:false,layout_approved:false};
fs.writeFileSync('checks/20261023/a4-sheet-export.json',JSON.stringify(manifest,null,2)+'\n');
console.log(`Exported ${pages.length} A4 sheets, ${covered.size} components, ${manifest.schematic_ports_covered} ports`);
