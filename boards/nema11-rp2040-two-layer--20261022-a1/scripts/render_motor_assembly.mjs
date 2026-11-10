// Render the unchanged native GLB with an explicitly whole-scene camera.
// This is a camera-only derivative, not a new circuit build or geometry edit.
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import { mat4, vec3 } from "gl-matrix";
import { renderGLTFToPNGFromGLB } from "poppygl";
import { Resvg } from "@resvg/resvg-js";
const input = process.argv[2] ?? "dist/assembly-preview/3d.glb";
const output =
  process.argv[3] ??
  "artifacts/motor-assembly-review/preliminary-full-assembly.png";
const glb = fs.readFileSync(input);
const hash = (b) => crypto.createHash("sha256").update(b).digest("hex");
if (glb.toString("ascii", 0, 4) !== "glTF") throw Error("Expected native GLB");
const gltf = JSON.parse(glb.toString("utf8", 20, 20 + glb.readUInt32LE(12)));
const lo = [Infinity, Infinity, Infinity],
  hi = [-Infinity, -Infinity, -Infinity];
function visit(id, parent) {
  const n = gltf.nodes[id];
  let local = mat4.create();
  if (n.matrix) local = mat4.fromValues(...n.matrix);
  else
    mat4.fromRotationTranslationScale(
      local,
      n.rotation ?? [0, 0, 0, 1],
      n.translation ?? [0, 0, 0],
      n.scale ?? [1, 1, 1],
    );
  const world = mat4.multiply(mat4.create(), parent, local);
  if (n.mesh !== undefined)
    for (const p of gltf.meshes[n.mesh].primitives) {
      const a = gltf.accessors[p.attributes.POSITION];
      if (!a.min || !a.max) throw Error("Missing position bounds");
      for (let i = 0; i < 8; i++) {
        const v = vec3.transformMat4(
          vec3.create(),
          [0, 1, 2].map((k) => (i & (1 << k) ? a.max[k] : a.min[k])),
          world,
        );
        for (let k = 0; k < 3; k++) {
          lo[k] = Math.min(lo[k], v[k]);
          hi[k] = Math.max(hi[k], v[k]);
        }
      }
    }
  for (const c of n.children ?? []) visit(c, world);
}
for (const n of gltf.scenes[gltf.scene ?? 0].nodes) visit(n, mat4.create());
const lookAt = lo.map((v, i) => (v + hi[i]) / 2);
const radius = Math.hypot(...hi.map((v, i) => (v - lo[i]) / 2));
const fov = 38;
// Bounding sphere fit at 1.15 margin, width >= height: contains every mesh.
const distance = (radius / Math.sin((fov * Math.PI) / 360)) * 1.15;
const direction = [0.95, 0.55, -1.5],
  length = Math.hypot(...direction);
const camPos = lookAt.map((v, i) => v + (distance * direction[i]) / length);
const options = {
  width: 1200,
  height: 1000,
  camPos,
  lookAt,
  up: "y+",
  fov,
  realistic: true,
  supersampling: 1,
  backgroundColor: "#edf1f5",
  grid: false,
};
const png = await renderGLTFToPNGFromGLB(glb, options);
const label = "PRELIMINARY · EXPLODED REVIEW · NOT FABRICATION-READY";
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1100"><rect width="1200" height="1100" fill="#edf1f5"/><image href="data:image/png;base64,${Buffer.from(png).toString("base64")}" x="0" y="70" width="1200" height="1000"/><text x="30" y="35" font-family="DejaVu Sans" font-size="23" font-weight="bold" fill="#203347">${label}</text><text x="30" y="62" font-family="DejaVu Sans" font-size="18" fill="#203347">Unchanged native motor + PCB geometry. 10 mm review gap is not an approved spacer or mounting stack.</text><text x="30" y="1083" font-family="DejaVu Sans" font-size="18" fill="#8c251c">OEM leads exceed the 28.3 mm frame target. Rear fasteners, insulation and harness remain unqualified.</text></svg>`;
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, new Resvg(svg).render().asPng());
if (hash(fs.readFileSync(input)) !== hash(glb))
  throw Error("Input GLB changed during render");
fs.writeFileSync(
  output + ".json",
  JSON.stringify(
    {
      scope:
        "Camera-only labeled render of unchanged native GLB; preliminary layout",
      input,
      input_sha256: hash(glb),
      output,
      output_sha256: hash(fs.readFileSync(output)),
      gltf_world_bounds: { min: lo, max: hi },
      camera: options,
      geometry_mutated: false,
      manufacturing_release: false,
    },
    null,
    2,
  ) + "\n",
);
console.log(JSON.stringify({ output, bounds: { lo, hi }, camPos, lookAt }));
