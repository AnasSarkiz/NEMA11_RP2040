import objPath from "./USB4145_03_0070_C.obj"
import stepPath from "./USB4145_03_0070_C.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["GND1","A1"],
  pin2: ["DP1","A6"],
  pin3: ["VBUS1","A4"],
  pin4: ["CC1","A5"],
  pin5: ["GND2","A12"],
  pin6: ["DN1","A7"],
  pin7: ["SBU1","A8"],
  pin8: ["VBUS2","A9"],
  pin9: ["GND3","B12"],
  pin10: ["DN2","B7"],
  pin11: ["VBUS3","B9"],
  pin12: ["SBU2","B8"],
  pin13: ["GND4","B1"],
  pin14: ["DP2","B6"],
  pin15: ["CC2","B5"],
  pin16: ["VBUS4","B4"],
  pin17: ["SHELL"]
} as const

export const USB4145_03_0070_C = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5815189"
  ]
}}
      manufacturerPartNumber="USB4145-03-0070-C"
      footprint={<footprint>
        <cutout shape="polygon" points={[{"x":4.377486800000042,"y":-0.35496499999999287},{"x":3.577488399999993,"y":-0.35496499999999287},{"x":3.786146521825458,"y":-0.2871678664400861},{"x":3.915104333142267,"y":-0.10967266644001938},{"x":3.915104333142267,"y":0.10972346643984565},{"x":3.786146521825458,"y":0.28721866643991234},{"x":3.577488399999993,"y":0.35501579999981914},{"x":4.377486800000042,"y":0.3550157999999328},{"x":4.168828678174464,"y":0.28721866643991234},{"x":4.039870866857768,"y":0.10972346643984565},{"x":4.039870866857768,"y":-0.10967266644001938},{"x":4.168828678174464,"y":-0.2871678664400861},{"x":4.377486800000042,"y":-0.35496499999999287}]} />
<hole pcbX="-4.0224964mm" pcbY="0.000127mm" diameter="0.7099808mm" />
<platedhole  portHints={["pin17"]} pcbX="-4.0224964mm" pcbY="1.429893mm" holeWidth="0.5999988mm" holeHeight="1.0999978mm" outerWidth="1.0999978mm" outerHeight="1.5999968mm" pcbRotation="90deg" shape="pill" />
<platedhole  portHints={["pin17"]} pcbX="-4.0224964mm" pcbY="-1.429893mm" holeWidth="0.5999988mm" holeHeight="1.0999978mm" outerWidth="1.0999978mm" outerHeight="1.5999968mm" pcbRotation="90deg" shape="pill" />
<platedhole  portHints={["pin17"]} pcbX="3.9774876mm" pcbY="-1.429893mm" holeWidth="0.5999988mm" holeHeight="1.0999978mm" outerWidth="1.0999978mm" outerHeight="1.5999968mm" pcbRotation="90deg" shape="pill" />
<platedhole  portHints={["pin17"]} pcbX="3.9774876mm" pcbY="1.429893mm" holeWidth="0.5999988mm" holeHeight="1.0999978mm" outerWidth="1.0999978mm" outerHeight="1.5999968mm" pcbRotation="90deg" shape="pill" />
<smtpad portHints={["pin1"]} pcbX="-2.7725624mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.2724404mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-1.2724384mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-0.7725664mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="2.7275536mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="0.2274316mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="0.7275576mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="1.2274296mm" pcbY="1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-2.7723084mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-0.2724404mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-1.2724384mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="-0.7725664mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="2.7275536mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="0.2274316mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="0.7275576mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="1.2274296mm" pcbY="-1.479931mm" width="0.2999994mm" height="1.1500104mm" shape="rect" />
<silkscreenpath route={[{"x":-4.492498000000069,"y":0.7295895999998265},{"x":-4.492498000000069,"y":-0.7293356000001268}]} />
<silkscreenpath route={[{"x":1.6085820000000695,"y":-1.5798800000001165},{"x":2.346426600000086,"y":-1.5798800000001165}]} />
<silkscreenpath route={[{"x":-2.39115599999991,"y":-1.5798800000001165},{"x":-1.6535654000000477,"y":-1.5798800000001165}]} />
<silkscreenpath route={[{"x":4.457496799999944,"y":0.7346187999999074},{"x":4.457496799999944,"y":-0.734364800000094}]} />
<silkscreenpath route={[{"x":1.6085820000000695,"y":1.58013399999993},{"x":2.346426600000086,"y":1.58013399999993}]} />
<silkscreenpath route={[{"x":-2.3914100000000644,"y":1.58013399999993},{"x":-1.6535654000000477,"y":1.58013399999993}]} />
<silkscreentext text="{NAME}" pcbX="0.0488696mm" pcbY="3.046351mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-5.072494800000072,"y":2.3049361999998155},{"x":5.0274859999999535,"y":2.3049361999998155},{"x":5.0274859999999535,"y":-2.304936199999929},{"x":-5.072494800000072,"y":-2.304936199999929},{"x":-5.072494800000072,"y":2.3049361999998155}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.019988200000045975, y: 3.4270054999999795, z: -4.5927207999999995 },
      }}
      {...props}
    />
  )
}