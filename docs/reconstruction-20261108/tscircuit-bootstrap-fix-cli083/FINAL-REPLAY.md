# Final reconstructed placement replay

The final native input SHA-256 is `b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`. The adjacent `final-native-*` files preserve the fresh read-only replay using the same CLI analyzer 0.0.83 candidate described in REPORT.md.

The result remains three findings before the candidate and two afterward. Only C_BOOTSTRAP `TwoPinComponentShouldBeVertical` is removed. U_TEMP and D_STATUS label findings are identical; no findings are added. Input bytes were unchanged.

This does not install the patch, change board/import definitions, approve upstream integration, or make the board schematic gate pass. The production check still reports all three findings.
