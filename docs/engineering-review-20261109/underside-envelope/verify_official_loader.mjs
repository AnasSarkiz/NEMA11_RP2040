import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const board=path.resolve(process.argv[2]);
const {loadCadComponentMesh}=await import(pathToFileURL(path.join(board,'node_modules/circuit-json-to-gltf/dist/index.js')));
const circuit=JSON.parse(fs.readFileSync(path.join(board,'dist/index/circuit.json')));
const source=new Map(circuit.filter(x=>x.type==='source_component').map(x=>[x.source_component_id,x]));
const pcb=new Map(circuit.filter(x=>x.type==='pcb_component').map(x=>[x.pcb_component_id,x]));
const before=JSON.stringify(circuit);
const results=[];
for(const cad of circuit.filter(x=>x.type==='cad_component')) {
 if(!cad.model_obj_url?.startsWith('./imports/')) throw new Error('Expected local imported OBJ, no network load permitted');
 const mesh=await loadCadComponentMesh(cad,{pcbComponent:pcb.get(cad.pcb_component_id),projectBaseUrl:pathToFileURL(board+'/').href});
 const xyz=[0,1,2].map(axis=>mesh.positions.filter((_,i)=>i%3===axis));
 results.push({name:source.get(cad.source_component_id).name,vertex_count:mesh.positions.length/3,triangle_count:mesh.indices.length/3,
 min:xyz.map(values=>Math.min(...values)),max:xyz.map(values=>Math.max(...values))});
}
if(JSON.stringify(circuit)!==before)throw new Error('Input mutated');
fs.writeFileSync(path.join(path.dirname(new URL(import.meta.url).pathname),'official-loader-bounds.json'),JSON.stringify(results,null,2)+'\n');
console.log(`Loaded ${results.length} exact CAD records through official world-coordinate mesh loader, without modifying input`);
