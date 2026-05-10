(* Instrument-maker Wolfram notebook starter.
   Edit the association below, then run in Wolfram Desktop or Cloud. *)

ClearAll["Global`*"];

design = <|
  "Instrument" -> "Untitled instrument",
  "Units" -> "Imperial",
  "A4" -> 440,
  "SpeedOfSoundInPerSec" -> 13552,
  "Notes" -> {}
|>;

frequencyFromMidi[midi_, a4_: 440] := a4*2^((midi - 69)/12);
centsError[measured_, target_] := 1200*Log2[measured/target];
openPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(2*freq) - 2*0.6*radius;
stoppedPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(4*freq) - 0.6*radius;
cantileverLengthIn[freq_, thickness_, k_] := Sqrt[k*thickness/freq];

CreateDocument[
  {
    TextCell[design["Instrument"], "Title"],
    TextCell["Instrument-maker computational design notebook", "Subtitle"],
    ExpressionCell[design, "Input"],
    TextCell["Add Manipulate, plots, imported workbook data, and validation cells below.", "Text"]
  },
  WindowTitle -> design["Instrument"]
]
