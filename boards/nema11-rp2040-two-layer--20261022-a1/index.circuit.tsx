// WIP source construction. Native PCB routing is intentionally disabled.
// Supplier definitions are fresh JLCPCB imports; no footprint/symbol/pin/CAD overrides.
import poses from "./config/placement.json";
import requirements from "./config/requirements.json";
import { A_0402WGF1001TCE } from "./imports/A_0402WGF1001TCE/A_0402WGF1001TCE";
import { B4B_PH_K_S_LF__SN_ } from "./imports/B4B_PH_K_S_LF__SN_/B4B_PH_K_S_LF__SN_";
import { CL31A106KBHNNNE } from "./imports/CL31A106KBHNNNE/CL31A106KBHNNNE";
import { CL05B103KB5NNNC } from "./imports/CL05B103KB5NNNC/CL05B103KB5NNNC";
import { CL05B104KO5NNNC } from "./imports/CL05B104KO5NNNC/CL05B104KO5NNNC";
import { A_0402CG150J500NT } from "./imports/A_0402CG150J500NT/A_0402CG150J500NT";
import { CL10A105KB8NNNC } from "./imports/CL10A105KB8NNNC/CL10A105KB8NNNC";
import { CL10B103KB8NNNC } from "./imports/CL10B103KB8NNNC/CL10B103KB8NNNC";
import { TYPE_C_31_M_12 } from "./imports/TYPE_C_31_M_12/TYPE_C_31_M_12";
import { SMF18A } from "./imports/SMF18A/SMF18A";
import { CL10A106KP8NNNC } from "./imports/CL10A106KP8NNNC/CL10A106KP8NNNC";
import { RP2040 } from "./imports/RP2040/RP2040";
import { ABM8_272_T3 } from "./imports/ABM8_272_T3/ABM8_272_T3";
import { AO3400A } from "./imports/AO3400A/AO3400A";
import { CL10B224KA8NNNC } from "./imports/CL10B224KA8NNNC/CL10B224KA8NNNC";
import { A_0603WAF0000T5E } from "./imports/A_0603WAF0000T5E/A_0603WAF0000T5E";
import { A_0402WGF1000TCE } from "./imports/A_0402WGF1000TCE/A_0402WGF1000TCE";
import { A_0402WGF270JTCE } from "./imports/A_0402WGF270JTCE/A_0402WGF270JTCE";
import { A_0402WGF3300TCE } from "./imports/A_0402WGF3300TCE/A_0402WGF3300TCE";
import { A_0402WGF1003TCE } from "./imports/A_0402WGF1003TCE/A_0402WGF1003TCE";
import { A_0402WGF1002TCE } from "./imports/A_0402WGF1002TCE/A_0402WGF1002TCE";
import { A_0402WGF5602TCE } from "./imports/A_0402WGF5602TCE/A_0402WGF5602TCE";
import { A_0603WAF1003T5E } from "./imports/A_0603WAF1003T5E/A_0603WAF1003T5E";
import { A_0603WAF1002T5E } from "./imports/A_0603WAF1002T5E/A_0603WAF1002T5E";
import { A_0402WGF4701TCE } from "./imports/A_0402WGF4701TCE/A_0402WGF4701TCE";
import { A_0402WGF5101TCE } from "./imports/A_0402WGF5101TCE/A_0402WGF5101TCE";
import { USBLC6_2SC6 } from "./imports/USBLC6_2SC6/USBLC6_2SC6";
import { GD25Q16EEIGR } from "./imports/GD25Q16EEIGR/GD25Q16EEIGR";
import { A4988SETTR_T } from "./imports/A4988SETTR_T/A4988SETTR_T";
import { A_0603WAF2002T5E } from "./imports/A_0603WAF2002T5E/A_0603WAF2002T5E";
import { CH224A } from "./imports/CH224A/CH224A";
import { CL21A226MAQNNNE } from "./imports/CL21A226MAQNNNE/CL21A226MAQNNNE";
import { LTST_C19HE1WT } from "./imports/LTST_C19HE1WT/LTST_C19HE1WT";
import { PMEG6020ELRX } from "./imports/PMEG6020ELRX/PMEG6020ELRX";
import { DTC114EU3HZGT106 } from "./imports/DTC114EU3HZGT106/DTC114EU3HZGT106";
import { CL05A105KA5NQNC } from "./imports/CL05A105KA5NQNC/CL05A105KA5NQNC";
import { RVT1V470M0605 } from "./imports/RVT1V470M0605/RVT1V470M0605";
import { HP05W3F240LT5E } from "./imports/HP05W3F240LT5E/HP05W3F240LT5E";
import { SRN4018_4R7M } from "./imports/SRN4018_4R7M/SRN4018_4R7M";
import { AP63203WU_7 } from "./imports/AP63203WU_7/AP63203WU_7";
import { AS5600_ASOM } from "./imports/AS5600_ASOM/AS5600_ASOM";
import { B5819W_SL } from "./imports/B5819W_SL/B5819W_SL";
import { MLT_5020 } from "./imports/MLT_5020/MLT_5020";
import { CL05B104KB5NNNC } from "./imports/CL05B104KB5NNNC/CL05B104KB5NNNC";
import { XL_1608SURC_06 } from "./imports/XL_1608SURC_06/XL_1608SURC_06";
import { TMP102AIDRLR } from "./imports/TMP102AIDRLR/TMP102AIDRLR";

const position = (name: keyof typeof poses.placements) => ({
  ...poses.placements[name],
  layer: poses.placements[name].layer as "top" | "bottom",
});

export default function Nema11TwoLayerBuzzer() {
  return (
    <board
      width={28}
      height={28}
      thickness={1.6}
      layers={2}
      routingDisabled={true}
      schAutoLayoutEnabled={false}
      minTraceWidth={0.16}
      minTraceToPadEdgeClearance={0.15}
      minPadEdgeToPadEdgeClearance={0.15}
      minBoardEdgeClearance={0.25}
      minViaHoleDiameter={0.3}
      minViaPadDiameter={0.45}
      minViaHoleEdgeToViaHoleEdgeClearance={0.2}
      minPlatedHoleDrillEdgeToDrillEdgeClearance={0.45}
    >
      <net name="A_MINUS" nominalTraceWidth={0.3} />
      <net name="A_PLUS" nominalTraceWidth={0.3} />
      <net name="BOOT_PAD" nominalTraceWidth={0.16} />
      <net name="BUCK_BST" nominalTraceWidth={0.16} />
      <net name="BUCK_SW" nominalTraceWidth={0.16} />
      <net name="BUZZER_GATE" nominalTraceWidth={0.16} />
      <net name="BUZZER_PWM" nominalTraceWidth={0.16} />
      <net name="BUZZER_SINK" nominalTraceWidth={0.16} />
      <net name="B_MINUS" nominalTraceWidth={0.3} />
      <net name="B_PLUS" nominalTraceWidth={0.3} />
      <net name="CP1" nominalTraceWidth={0.16} />
      <net name="CP2" nominalTraceWidth={0.16} />
      <net name="DATA_CC1" nominalTraceWidth={0.16} />
      <net name="DATA_CC2" nominalTraceWidth={0.16} />
      <net name="DATA_PRESENT" nominalTraceWidth={0.16} />
      <net name="DATA_VBUS" isPowerNet={true} nominalTraceWidth={0.16} />
      <net name="DIR" nominalTraceWidth={0.16} />
      <net name="ENABLE_N" nominalTraceWidth={0.16} />
      <net name="GND" isGroundNet={true} nominalTraceWidth={0.16} />
      <net name="LED_B" nominalTraceWidth={0.16} />
      <net name="LED_G" nominalTraceWidth={0.16} />
      <net name="LED_R" nominalTraceWidth={0.16} />
      <net name="LOGIC_IN" isPowerNet={true} nominalTraceWidth={0.16} />
      <net name="MCU_DM" nominalTraceWidth={0.16} />
      <net name="MCU_DP" nominalTraceWidth={0.16} />
      <net name="PD_CC1" nominalTraceWidth={0.16} />
      <net name="PD_CC2" nominalTraceWidth={0.16} />
      <net name="PD_CFG" nominalTraceWidth={0.16} />
      <net name="PD_GOOD" nominalTraceWidth={0.16} />
      <net name="PD_VBUS" isPowerNet={true} nominalTraceWidth={0.3} />
      <net name="PD_VHV" isPowerNet={true} nominalTraceWidth={0.16} />
      <net name="PWR_LED_A" nominalTraceWidth={0.16} />
      <net name="QSPI_SCLK" nominalTraceWidth={0.16} />
      <net name="QSPI_SD0" nominalTraceWidth={0.16} />
      <net name="QSPI_SD1" nominalTraceWidth={0.16} />
      <net name="QSPI_SD2" nominalTraceWidth={0.16} />
      <net name="QSPI_SD3" nominalTraceWidth={0.16} />
      <net name="QSPI_SS" nominalTraceWidth={0.16} />
      <net name="RUN" nominalTraceWidth={0.16} />
      <net name="SENSE1" nominalTraceWidth={0.3} />
      <net name="SENSE2" nominalTraceWidth={0.3} />
      <net name="SLEEP" nominalTraceWidth={0.16} />
      <net name="STATUS_B_C" nominalTraceWidth={0.16} />
      <net name="STATUS_B_K" nominalTraceWidth={0.16} />
      <net name="STATUS_G_C" nominalTraceWidth={0.16} />
      <net name="STATUS_G_K" nominalTraceWidth={0.16} />
      <net name="STATUS_R_C" nominalTraceWidth={0.16} />
      <net name="STATUS_R_K" nominalTraceWidth={0.16} />
      <net name="STEP" nominalTraceWidth={0.16} />
      <net name="SWCLK" nominalTraceWidth={0.16} />
      <net name="SWDIO" nominalTraceWidth={0.16} />
      <net name="TEMP_SCL" nominalTraceWidth={0.16} />
      <net name="TEMP_SDA" nominalTraceWidth={0.16} />
      <net name="USB_DM" nominalTraceWidth={0.16} />
      <net name="USB_DP" nominalTraceWidth={0.16} />
      <net name="V1V1" isPowerNet={true} nominalTraceWidth={0.16} />
      <net name="V3V3" isPowerNet={true} nominalTraceWidth={0.16} />
      <net name="VCP" nominalTraceWidth={0.16} />
      <net name="VM_SENSE" nominalTraceWidth={0.16} />
      <net name="VREF" nominalTraceWidth={0.16} />
      <net name="VREG" nominalTraceWidth={0.16} />
      <net name="XIN" nominalTraceWidth={0.16} />
      <net name="XOUT" nominalTraceWidth={0.16} />
      <net name="XTAL_OUT" nominalTraceWidth={0.16} />
      <hole
        name="M1"
        pcbX={-11.5}
        pcbY={-11.5}
        diameter={requirements.provisional_hole_diameter_mm}
      />
      <keepout
        pcbX={-11.5}
        pcbY={-11.5}
        shape="circle"
        radius={requirements.provisional_head_exclusion_radius_mm}
        layers={["top", "bottom"]}
        allowPlacements={false}
      />
      <hole
        name="M2"
        pcbX={-11.5}
        pcbY={11.5}
        diameter={requirements.provisional_hole_diameter_mm}
      />
      <keepout
        pcbX={-11.5}
        pcbY={11.5}
        shape="circle"
        radius={requirements.provisional_head_exclusion_radius_mm}
        layers={["top", "bottom"]}
        allowPlacements={false}
      />
      <hole
        name="M3"
        pcbX={11.5}
        pcbY={-11.5}
        diameter={requirements.provisional_hole_diameter_mm}
      />
      <keepout
        pcbX={11.5}
        pcbY={-11.5}
        shape="circle"
        radius={requirements.provisional_head_exclusion_radius_mm}
        layers={["top", "bottom"]}
        allowPlacements={false}
      />
      <hole
        name="M4"
        pcbX={11.5}
        pcbY={11.5}
        diameter={requirements.provisional_hole_diameter_mm}
      />
      <keepout
        pcbX={11.5}
        pcbY={11.5}
        shape="circle"
        radius={requirements.provisional_head_exclusion_radius_mm}
        layers={["top", "bottom"]}
        allowPlacements={false}
      />
      <schematicsheet
        name="01 Power &amp; USB-PD"
        sheetIndex={0}
        sheetSize="A4"
      >
        <TYPE_C_31_M_12
          name="J_PD"
          {...position("J_PD")}
          schX={4}
          schY={14.8}
          noConnect={["pin5", "pin11", "pin7", "pin8", "pin9", "pin10"]}
          connections={{
            pin1: "net.GND",
            pin2: "net.GND",
            pin3: "net.GND",
            pin4: "net.GND",
            pin13: "net.GND",
            pin14: "net.GND",
            pin6: "net.PD_CC1",
            pin12: "net.PD_CC2",
            pin15: "net.PD_VBUS",
            pin16: "net.PD_VBUS",
          }}
        />
        <CH224A
          name="U_PD"
          {...position("U_PD")}
          schX={11}
          schY={15.72}
          noConnect={["pin2", "pin3", "pin4", "pin5"]}
          connections={{
            pin1: "net.PD_VHV",
            pin6: "net.PD_CC2",
            pin7: "net.PD_CC1",
            pin8: "net.PD_VBUS",
            pin9: "net.PD_CFG",
            pin10: "net.PD_GOOD",
            pin11: "net.GND",
          }}
        />
        <A_0402WGF5602TCE
          name="R_PD_CFG"
          {...position("R_PD_CFG")}
          schX={15.9}
          schY={10.2}
          connections={{ pin1: "net.PD_CFG", pin2: "net.GND" }}
        />
        <A_0603WAF0000T5E
          name="R_PD"
          {...position("R_PD")}
          schX={9.8}
          schY={10.2}
          connections={{ pin1: "net.PD_VBUS", pin2: "net.PD_VHV" }}
        />
        <CL10A105KB8NNNC
          name="C_PD"
          {...position("C_PD")}
          schX={12.7}
          schY={10.2}
          connections={{ pin1: "net.PD_VHV", pin2: "net.GND" }}
        />
        <A_0603WAF1002T5E
          name="R_PG"
          {...position("R_PG")}
          schX={14.5}
          schY={15.5}
          connections={{ pin1: "net.V3V3", pin2: "net.PD_GOOD" }}
        />
        <SMF18A
          name="D_TVS"
          {...position("D_TVS")}
          schX={4}
          schY={9.2}
          connections={{ pin2: "net.PD_VBUS", pin1: "net.GND" }}
        />
        <B5819W_SL
          name="D_PD"
          {...position("D_PD")}
          schX={19.2}
          schY={16.8}
          connections={{ pin1: "net.LOGIC_IN", pin2: "net.PD_VBUS" }}
        />
        <B5819W_SL
          name="D_DATA"
          {...position("D_DATA")}
          schX={19.2}
          schY={14.5}
          connections={{ pin1: "net.LOGIC_IN", pin2: "net.DATA_VBUS" }}
        />
        <AP63203WU_7
          name="U_BUCK"
          {...position("U_BUCK")}
          schX={24}
          schY={13.2}
          connections={{
            pin1: "net.V3V3",
            pin2: "net.LOGIC_IN",
            pin3: "net.LOGIC_IN",
            pin4: "net.GND",
            pin5: "net.BUCK_SW",
            pin6: "net.BUCK_BST",
          }}
        />
        <SRN4018_4R7M
          name="L_BUCK"
          {...position("L_BUCK")}
          schX={28.2}
          schY={13.2}
          connections={{ pin1: "net.BUCK_SW", pin2: "net.V3V3" }}
        />
        <CL05B104KO5NNNC
          name="C_BOOTSTRAP"
          {...position("C_BOOTSTRAP")}
          schX={26.5}
          schY={15.2}
          connections={{ pin1: "net.BUCK_BST", pin2: "net.BUCK_SW" }}
        />
        <CL31A106KBHNNNE
          name="C_BUCK_IN"
          {...position("C_BUCK_IN")}
          schX={21}
          schY={9.5}
          connections={{ pin1: "net.LOGIC_IN", pin2: "net.GND" }}
        />
        <CL21A226MAQNNNE
          name="C_BUCK_OUT1"
          {...position("C_BUCK_OUT1")}
          schX={27}
          schY={9.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL21A226MAQNNNE
          name="C_BUCK_OUT2"
          {...position("C_BUCK_OUT2")}
          schX={29.1}
          schY={9.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
      </schematicsheet>
      <schematicsheet
        name="02 Programming &amp; USB"
        sheetIndex={1}
        sheetSize="A4"
      >
        <TYPE_C_31_M_12
          name="J_DATA"
          {...position("J_DATA")}
          schX={4}
          schY={14.1}
          noConnect={["pin5", "pin11"]}
          connections={{
            pin1: "net.GND",
            pin2: "net.GND",
            pin3: "net.GND",
            pin4: "net.GND",
            pin13: "net.GND",
            pin14: "net.GND",
            pin6: "net.DATA_CC1",
            pin12: "net.DATA_CC2",
            pin15: "net.DATA_VBUS",
            pin16: "net.DATA_VBUS",
            pin7: "net.USB_DM",
            pin9: "net.USB_DM",
            pin8: "net.USB_DP",
            pin10: "net.USB_DP",
          }}
        />
        <A_0402WGF5101TCE
          name="R_CC1"
          {...position("R_CC1")}
          schX={8.3}
          schY={16.4}
          connections={{ pin1: "net.DATA_CC1", pin2: "net.GND" }}
        />
        <A_0402WGF5101TCE
          name="R_CC2"
          {...position("R_CC2")}
          schX={11}
          schY={16.4}
          connections={{ pin1: "net.DATA_CC2", pin2: "net.GND" }}
        />
        <USBLC6_2SC6
          name="U_ESD"
          {...position("U_ESD")}
          schX={10}
          schY={11.3}
          connections={{
            pin1: "net.USB_DP",
            pin2: "net.GND",
            pin3: "net.USB_DM",
            pin4: "net.USB_DM",
            pin5: "net.DATA_VBUS",
            pin6: "net.USB_DP",
          }}
        />
        <A_0402WGF270JTCE
          name="R_DP"
          {...position("R_DP")}
          schX={15.4}
          schY={11.85}
          connections={{ pin1: "net.MCU_DP", pin2: "net.USB_DP" }}
        />
        <A_0402WGF270JTCE
          name="R_DM"
          {...position("R_DM")}
          schX={15.4}
          schY={10.75}
          connections={{ pin1: "net.MCU_DM", pin2: "net.USB_DM" }}
        />
        <A_0402WGF1003TCE
          name="R_USB_SENSE_H"
          {...position("R_USB_SENSE_H")}
          schX={4}
          schY={6.2}
          connections={{ pin1: "net.DATA_VBUS", pin2: "net.DATA_PRESENT" }}
        />
        <A_0402WGF1003TCE
          name="R_USB_SENSE_L"
          {...position("R_USB_SENSE_L")}
          schX={4}
          schY={3.8}
          connections={{ pin1: "net.DATA_PRESENT", pin2: "net.GND" }}
        />
        <GD25Q16EEIGR
          name="U_FLASH"
          {...position("U_FLASH")}
          schX={24.5}
          schY={14.6}
          connections={{
            pin1: "net.QSPI_SS",
            pin2: "net.QSPI_SD1",
            pin3: "net.QSPI_SD2",
            pin4: "net.GND",
            pin5: "net.QSPI_SD0",
            pin6: "net.QSPI_SCLK",
            pin7: "net.QSPI_SD3",
            pin8: "net.V3V3",
            pin9: "net.GND",
          }}
        />
        <CL05B104KO5NNNC
          name="C_FLASH"
          {...position("C_FLASH")}
          schX={29.8}
          schY={14.8}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <A_0402WGF1002TCE
          name="R_FLASH_CS"
          {...position("R_FLASH_CS")}
          schX={20}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.QSPI_SS" }}
        />
        <A_0402WGF1001TCE
          name="R_BOOT"
          {...position("R_BOOT")}
          schX={23.5}
          schY={7}
          connections={{ pin1: "net.QSPI_SS", pin2: "net.BOOT_PAD" }}
        />
        <testpoint
          name="TP_BOOT"
          {...position("TP_BOOT")}
          schX={27}
          schY={7}
          doNotPlace={true}
          connections={{ pin1: "net.BOOT_PAD" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
        <testpoint
          name="TP_BOOT_GND"
          {...position("TP_BOOT_GND")}
          schX={27}
          schY={5.5}
          doNotPlace={true}
          connections={{ pin1: "net.GND" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
      </schematicsheet>
      <schematicsheet
        name="03 Controller &amp; clocks"
        sheetIndex={2}
        sheetSize="A4"
      >
        <RP2040
          name="U_MCU"
          {...position("U_MCU")}
          schX={9.5}
          schY={11.5}
          noConnect={[
            "pin2",
            "pin3",
            "pin6",
            "pin7",
            "pin14",
            "pin15",
            "pin16",
            "pin17",
            "pin18",
            "pin28",
            "pin29",
            "pin30",
            "pin31",
            "pin32",
            "pin34",
            "pin35",
            "pin36",
          ]}
          connections={{
            pin1: "net.V3V3",
            pin4: "net.LED_G",
            pin5: "net.LED_B",
            pin8: "net.STEP",
            pin9: "net.DIR",
            pin10: "net.V3V3",
            pin11: "net.ENABLE_N",
            pin12: "net.SLEEP",
            pin13: "net.PD_GOOD",
            pin19: "net.GND",
            pin20: "net.XIN",
            pin21: "net.XOUT",
            pin22: "net.V3V3",
            pin23: "net.V1V1",
            pin24: "net.SWCLK",
            pin25: "net.SWDIO",
            pin26: "net.RUN",
            pin27: "net.BUZZER_PWM",
            pin33: "net.V3V3",
            pin37: "net.LED_R",
            pin38: "net.TEMP_SDA",
            pin39: "net.TEMP_SCL",
            pin40: "net.VM_SENSE",
            pin41: "net.DATA_PRESENT",
            pin42: "net.V3V3",
            pin43: "net.V3V3",
            pin44: "net.V3V3",
            pin45: "net.V1V1",
            pin46: "net.MCU_DM",
            pin47: "net.MCU_DP",
            pin48: "net.V3V3",
            pin49: "net.V3V3",
            pin50: "net.V1V1",
            pin51: "net.QSPI_SD3",
            pin52: "net.QSPI_SCLK",
            pin53: "net.QSPI_SD0",
            pin54: "net.QSPI_SD2",
            pin55: "net.QSPI_SD1",
            pin56: "net.QSPI_SS",
            pin57: "net.GND",
          }}
        />
        <ABM8_272_T3
          name="Y_MCU"
          {...position("Y_MCU")}
          schX={23}
          schY={16.5}
          connections={{
            pin1: "net.XIN",
            pin3: "net.XTAL_OUT",
            pin4: "net.GND",
            pin2: "net.GND",
          }}
        />
        <A_0402WGF1001TCE
          name="R_XOUT"
          {...position("R_XOUT")}
          schX={27.5}
          schY={16.4875}
          connections={{ pin1: "net.XOUT", pin2: "net.XTAL_OUT" }}
        />
        <A_0402CG150J500NT
          name="C_XIN"
          {...position("C_XIN")}
          schX={19.5}
          schY={16}
          connections={{ pin1: "net.XIN", pin2: "net.GND" }}
        />
        <A_0402CG150J500NT
          name="C_XOUT"
          {...position("C_XOUT")}
          schX={25.5}
          schY={16}
          connections={{ pin1: "net.XTAL_OUT", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO1"
          {...position("C_IO1")}
          schX={17.3}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO10"
          {...position("C_IO10")}
          schX={19.400000000000002}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO22"
          {...position("C_IO22")}
          schX={21.5}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO33"
          {...position("C_IO33")}
          schX={23.6}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO42"
          {...position("C_IO42")}
          schX={25.700000000000003}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_IO49"
          {...position("C_IO49")}
          schX={27.8}
          schY={11.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_ADC"
          {...position("C_ADC")}
          schX={17.3}
          schY={7.8}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_USB"
          {...position("C_USB")}
          schX={19.400000000000002}
          schY={7.8}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05A105KA5NQNC
          name="C_VREG_IN"
          {...position("C_VREG_IN")}
          schX={21.5}
          schY={7.8}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05A105KA5NQNC
          name="C_VREG_OUT"
          {...position("C_VREG_OUT")}
          schX={17.3}
          schY={3.5}
          connections={{ pin1: "net.V1V1", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_DV23"
          {...position("C_DV23")}
          schX={19.400000000000002}
          schY={3.5}
          connections={{ pin1: "net.V1V1", pin2: "net.GND" }}
        />
        <CL05B104KO5NNNC
          name="C_DV50"
          {...position("C_DV50")}
          schX={21.5}
          schY={3.5}
          connections={{ pin1: "net.V1V1", pin2: "net.GND" }}
        />
        <A_0402WGF1002TCE
          name="R_RUN"
          {...position("R_RUN")}
          schX={3}
          schY={10.1}
          connections={{ pin1: "net.V3V3", pin2: "net.RUN" }}
        />
        <testpoint
          name="TP_3V3"
          {...position("TP_3V3")}
          schX={2}
          schY={6.5}
          doNotPlace={true}
          connections={{ pin1: "net.V3V3" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
        <testpoint
          name="TP_GND"
          {...position("TP_GND")}
          schX={4.5}
          schY={6.5}
          doNotPlace={true}
          connections={{ pin1: "net.GND" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
        <testpoint
          name="TP_SWCLK"
          {...position("TP_SWCLK")}
          schX={2}
          schY={5}
          doNotPlace={true}
          connections={{ pin1: "net.SWCLK" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
        <testpoint
          name="TP_SWDIO"
          {...position("TP_SWDIO")}
          schX={2}
          schY={3.5}
          doNotPlace={true}
          connections={{ pin1: "net.SWDIO" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
        <testpoint
          name="TP_RUN"
          {...position("TP_RUN")}
          schX={4.5}
          schY={3.5}
          doNotPlace={true}
          connections={{ pin1: "net.RUN" }}
          footprintVariant="pad"
          padDiameter="1.1mm"
        />
      </schematicsheet>
      <schematicsheet
        name="04 Stepper motor driver"
        sheetIndex={3}
        sheetSize="A4"
      >
        <A4988SETTR_T
          name="U_DRV"
          {...position("U_DRV")}
          schX={15.5}
          schY={12.3}
          noConnect={["pin7", "pin20", "pin25"]}
          connections={{
            pin1: "net.B_MINUS",
            pin2: "net.ENABLE_N",
            pin3: "net.GND",
            pin4: "net.CP1",
            pin5: "net.CP2",
            pin6: "net.VCP",
            pin8: "net.VREG",
            pin9: "net.V3V3",
            pin10: "net.V3V3",
            pin11: "net.V3V3",
            pin12: "net.V3V3",
            pin13: "net.GND",
            pin14: "net.SLEEP",
            pin15: "net.V3V3",
            pin16: "net.STEP",
            pin17: "net.VREF",
            pin18: "net.GND",
            pin19: "net.DIR",
            pin21: "net.A_MINUS",
            pin22: "net.PD_VBUS",
            pin23: "net.SENSE1",
            pin24: "net.A_PLUS",
            pin26: "net.B_PLUS",
            pin27: "net.SENSE2",
            pin28: "net.PD_VBUS",
            pin29: "net.GND",
          }}
        />
        <B4B_PH_K_S_LF__SN_
          name="J_MOTOR"
          {...position("J_MOTOR")}
          schX={28}
          schY={13.91}
          connections={{
            pin1: "net.A_PLUS",
            pin2: "net.A_MINUS",
            pin3: "net.B_PLUS",
            pin4: "net.B_MINUS",
          }}
        />
        <HP05W3F240LT5E
          name="R_SA"
          {...position("R_SA")}
          schX={22}
          schY={10.9}
          connections={{ pin1: "net.SENSE1", pin2: "net.GND" }}
        />
        <HP05W3F240LT5E
          name="R_SB"
          {...position("R_SB")}
          schX={25.8}
          schY={10.9}
          connections={{ pin1: "net.SENSE2", pin2: "net.GND" }}
        />
        <CL05B104KB5NNNC
          name="C_CP"
          {...position("C_CP")}
          schX={23}
          schY={8.4}
          connections={{ pin1: "net.CP1", pin2: "net.CP2" }}
        />
        <CL05B104KB5NNNC
          name="C_VCP"
          {...position("C_VCP")}
          schX={27.5}
          schY={8.4}
          connections={{ pin1: "net.VCP", pin2: "net.PD_VBUS" }}
        />
        <CL10B224KA8NNNC
          name="C_VREG"
          {...position("C_VREG")}
          schX={29.5}
          schY={5.2}
          connections={{ pin1: "net.VREG", pin2: "net.GND" }}
        />
        <CL05B104KB5NNNC
          name="C_VM"
          {...position("C_VM")}
          schX={3}
          schY={16.5}
          connections={{ pin1: "net.PD_VBUS", pin2: "net.GND" }}
        />
        <RVT1V470M0605
          name="C_BULK"
          {...position("C_BULK")}
          schX={5.1}
          schY={16.5}
          connections={{ pin2: "net.GND", pin1: "net.PD_VBUS" }}
        />
        <CL05B104KO5NNNC
          name="C_DRV_LOGIC"
          {...position("C_DRV_LOGIC")}
          schX={8.5}
          schY={16.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <A_0603WAF2002T5E
          name="R_REF_H"
          {...position("R_REF_H")}
          schX={3}
          schY={11}
          connections={{ pin1: "net.V3V3", pin2: "net.VREF" }}
        />
        <A_0402WGF1002TCE
          name="R_REF_L"
          {...position("R_REF_L")}
          schX={3}
          schY={8.6}
          connections={{ pin1: "net.VREF", pin2: "net.GND" }}
        />
        <CL10B103KB8NNNC
          name="C_REF"
          {...position("C_REF")}
          schX={6.8}
          schY={8.6}
          connections={{ pin1: "net.VREF", pin2: "net.GND" }}
        />
        <A_0402WGF1003TCE
          name="R_ENABLE"
          {...position("R_ENABLE")}
          schX={9}
          schY={11.8}
          connections={{ pin1: "net.V3V3", pin2: "net.ENABLE_N" }}
        />
        <A_0603WAF1003T5E
          name="R_SLEEP"
          {...position("R_SLEEP")}
          schX={9}
          schY={8.8}
          connections={{ pin1: "net.SLEEP", pin2: "net.GND" }}
        />
        <A_0402WGF1003TCE
          name="R_VM_H"
          {...position("R_VM_H")}
          schX={3}
          schY={4.9}
          connections={{ pin1: "net.PD_VBUS", pin2: "net.VM_SENSE" }}
        />
        <A_0402WGF1002TCE
          name="R_VM_L"
          {...position("R_VM_L")}
          schX={7}
          schY={4.9}
          connections={{ pin1: "net.VM_SENSE", pin2: "net.GND" }}
        />
        <CL05B103KB5NNNC
          name="C_VM_SENSE"
          {...position("C_VM_SENSE")}
          schX={10.5}
          schY={4.9}
          connections={{ pin1: "net.VM_SENSE", pin2: "net.GND" }}
        />
      </schematicsheet>
      <schematicsheet
        name="05 Temperature &amp; feedback"
        sheetIndex={4}
        sheetSize="A4"
      >
        <TMP102AIDRLR
          name="U_TEMP"
          {...position("U_TEMP")}
          schX={5.2}
          schY={15.5}
          noConnect={["pin3"]}
          connections={{
            pin1: "net.TEMP_SCL",
            pin2: "net.GND",
            pin4: "net.GND",
            pin5: "net.V3V3",
            pin6: "net.TEMP_SDA",
          }}
        />
        <CL05B104KO5NNNC
          name="C_TEMP"
          {...position("C_TEMP")}
          schX={10.8}
          schY={15.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <A_0402WGF4701TCE
          name="R_TEMP_SDA"
          {...position("R_TEMP_SDA")}
          schX={2.3}
          schY={11.5}
          connections={{ pin1: "net.TEMP_SDA", pin2: "net.V3V3" }}
        />
        <A_0402WGF4701TCE
          name="R_TEMP_SCL"
          {...position("R_TEMP_SCL")}
          schX={6.3}
          schY={11.5}
          connections={{ pin1: "net.TEMP_SCL", pin2: "net.V3V3" }}
        />
        <LTST_C19HE1WT
          name="D_STATUS"
          {...position("D_STATUS")}
          schX={25.3}
          schY={17.3}
          connections={{
            pin1: "net.STATUS_R_K",
            pin2: "net.STATUS_G_K",
            pin3: "net.STATUS_B_K",
            pin4: "net.DATA_VBUS",
          }}
        />
        <A_0402WGF1001TCE
          name="R_STATUS_R"
          {...position("R_STATUS_R")}
          schX={22}
          schY={14.8}
          connections={{ pin1: "net.STATUS_R_K", pin2: "net.STATUS_R_C" }}
        />
        <DTC114EU3HZGT106
          name="Q_STATUS_R"
          {...position("Q_STATUS_R")}
          schX={21.6375}
          schY={12.7}
          connections={{
            pin3: "net.STATUS_R_C",
            pin1: "net.GND",
            pin2: "net.LED_R",
          }}
        />
        <A_0402WGF1001TCE
          name="R_STATUS_G"
          {...position("R_STATUS_G")}
          schX={25.3}
          schY={14.8}
          connections={{ pin1: "net.STATUS_G_K", pin2: "net.STATUS_G_C" }}
        />
        <DTC114EU3HZGT106
          name="Q_STATUS_G"
          {...position("Q_STATUS_G")}
          schX={24.9375}
          schY={12.7}
          connections={{
            pin3: "net.STATUS_G_C",
            pin1: "net.GND",
            pin2: "net.LED_G",
          }}
        />
        <A_0402WGF1001TCE
          name="R_STATUS_B"
          {...position("R_STATUS_B")}
          schX={28.6}
          schY={14.8}
          connections={{ pin1: "net.STATUS_B_K", pin2: "net.STATUS_B_C" }}
        />
        <DTC114EU3HZGT106
          name="Q_STATUS_B"
          {...position("Q_STATUS_B")}
          schX={28.2375}
          schY={12.7}
          connections={{
            pin3: "net.STATUS_B_C",
            pin1: "net.GND",
            pin2: "net.LED_B",
          }}
        />
        <MLT_5020
          name="BZ1"
          {...position("BZ1")}
          schX={9.4}
          schY={6.5}
          noConnect={["pin3"]}
          connections={{ pin1: "net.V3V3", pin2: "net.BUZZER_SINK" }}
        />
        <AO3400A
          name="Q_BUZZER"
          {...position("Q_BUZZER")}
          schX={8.5}
          schY={3.8}
          connections={{
            pin3: "net.BUZZER_SINK",
            pin1: "net.BUZZER_GATE",
            pin2: "net.GND",
          }}
        />
        <A_0402WGF1000TCE
          name="R_BUZZER_GATE"
          {...position("R_BUZZER_GATE")}
          schX={3.8}
          schY={4.6}
          connections={{ pin1: "net.BUZZER_PWM", pin2: "net.BUZZER_GATE" }}
        />
        <A_0402WGF1003TCE
          name="R_BUZZER_PD"
          {...position("R_BUZZER_PD")}
          schX={5.8}
          schY={3.6}
          connections={{ pin1: "net.BUZZER_GATE", pin2: "net.GND" }}
        />
        <PMEG6020ELRX
          name="D_BUZZER"
          {...position("D_BUZZER")}
          schX={14}
          schY={6.5}
          connections={{ pin1: "net.V3V3", pin2: "net.BUZZER_SINK" }}
        />
        <CL10A106KP8NNNC
          name="C_BUZZER"
          {...position("C_BUZZER")}
          schX={17}
          schY={6.5}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <A_0402WGF3300TCE
          name="R_PWR_LED"
          {...position("R_PWR_LED")}
          schX={25}
          schY={6.2}
          connections={{ pin1: "net.V3V3", pin2: "net.PWR_LED_A" }}
        />
        <XL_1608SURC_06
          name="D_PWR"
          {...position("D_PWR")}
          schX={25}
          schY={3.8}
          connections={{ pin1: "net.GND", pin2: "net.PWR_LED_A" }}
        />
      </schematicsheet>
      <schematicsheet
        name="06 Optional encoder (DNP)"
        sheetIndex={5}
        sheetSize="A4"
      >
        <AS5600_ASOM
          name="U_ENCODER"
          {...position("U_ENCODER")}
          schX={9}
          schY={13}
          doNotPlace={true}
          noConnect={["pin3", "pin5"]}
          connections={{
            pin1: "net.V3V3",
            pin2: "net.V3V3",
            pin4: "net.GND",
            pin6: "net.TEMP_SDA",
            pin7: "net.TEMP_SCL",
            pin8: "net.GND",
          }}
        />
        <CL05B104KO5NNNC
          name="C_ENCODER"
          {...position("C_ENCODER")}
          schX={19}
          schY={13}
          doNotPlace={true}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
        <CL05A105KA5NQNC
          name="C_ENCODER_BULK"
          {...position("C_ENCODER_BULK")}
          schX={21.1}
          schY={13}
          doNotPlace={true}
          connections={{ pin1: "net.V3V3", pin2: "net.GND" }}
        />
      </schematicsheet>
    </board>
  );
}
