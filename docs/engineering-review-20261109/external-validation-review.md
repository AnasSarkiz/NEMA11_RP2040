# Build request review and retry evidence

The first copied-board native milestone invocation reached `Generating circuit JSON...` and its status poll was denied because an api.tscircuit.com request might transmit private source/layout. No fresh native output existed. The prior stock-only description is superseded: installed core can also fetch public supplier/datasheet validation metadata.

Read-only source verification:
- CLI build.worker.js `getPlatformConfigWithCliDefaults` sets checkAvailability:true.
- Core0.0.2304 component availability passes only supplierName/supplierPartNumber. Eval's fetchJlcPartAvailability normalizes public C-numbers and performs GET `https://jlcsearch.tscircuit.com/api/search?q=C...&limit=1` with cache/signal options and no body.
- Core NormalComponent_fetchDatasheetForValidation (dist/index.js lines633–684) can request validation metadata for Chip/PushButton/OpAmp. fetchPartCircuitJsonWithDatasheet passes supplierPartNumber/manufacturerPartNumber and sets includeDatasheetInformation.
- Eval JlcPcbPartsEngine fetchPartCircuitJson uses public EasyEDA part lookup then enrichPartCircuitJsonWithDatasheet. Its createDatasheetInformationLoader constructs GET `https://api.tscircuit.com/datasheets/get?chip_name=<normalized manufacturer part>` (eval dist/lib/index.js lines30252–30285), passing signal only. It sends no board/source/layout body.
- Supplier footprint/orientation comparisons call fetchPartCircuitJsonWithoutDatasheet with supplier part number; local copper comparison stays local.
- Isolated invocation has no TSCIRCUIT_* environment overrides and no isolated XDG config files. Board JSON config contains only included/preview file paths. Imported TSX contains no HTTP URLs; models are local OBJ/STEP imports. Board routingDisabled remains true. No telemetry/analytics/Sentry/PostHog references were found in the build worker. CLI's other literal api.tscircuit.com reference is an autorouter bug-report view URL, not a request in this unrouted build.
- Entire copied dependency tree matches production bytes except the expressly patched one-line core dist/index.js. No external symlinks exist in the copied board. Baseline native SHA256 is b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51.

After parent reviewed this materially new evidence, original process outcome was checked: its milestone exclusive lock was no longer held and status tool returned `Unknown process id 43060`. No fresh JSON or completion receipt existed. Therefore a single normal milestone retry was started. No endpoint, check, board configuration or execution route was changed. An exact request trace for the rejected event is not available; the source trace establishes the public metadata path but does not pretend to capture its runtime URL.
