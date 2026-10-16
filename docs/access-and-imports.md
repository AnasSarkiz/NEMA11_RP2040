# Native CLI authorization and exact supplier imports

## Authorization

Run `python3 scripts/tscircuit_login.py` from this checkout. It invokes the
native `tsci auth login`, prints the actual browser authorization URL, and keeps
polling for authorization. Use that generated URL, sign in to the intended
tscircuit account, and approve the CLI session. Do not paste a token into chat.

The wrapper suppresses all other native output because this CLI can print a
raw session token in npmrc fallback instructions when the home directory is
read-only. CLI credentials stay under `/workspace/.config`, outside the checkout.
The sign-in page `https://tscircuit.com/login` is not itself a CLI authorization
link. The registry must issue a session-specific link first.

The current runtime policy denies `registry-api.tscircuit.com` with HTTP 403.
The native login was attempted; no authorization link was issued. The saved
draft is not applied: observed runtime spec revision remains 1 with no custom
allowed domains or injected tscircuit credential. Review, save and publish the
pending environment settings to activate required access, then run the wrapper.

## Exact JLCPCB imports

Use native `tsci import --jlcpcb --download --use-exact-footprint C<number>`.
The exact-footprint option preserves supplier land geometry instead of replacing
it with a similar generic footprint. Download original STEP/OBJ, retain import
source and record file hashes, exact MPN, package and supplier identity. A
downloaded part does not establish stock, ratings, pin mapping or pickup rotation.

The C2040/RP2040 import was attempted in an external cache staging directory,
outside the project. JLC search and EasyEDA import were denied. The CLI calls
the EasyEDA HTTP 403 a rate limit; the enforced network policy and the JLC
response show a destination-access blocker. Do not retry on a timer or treat
the error message as evidence that the supplier part is unavailable.

The native CLI uses these exact destinations, now included in the draft:

| Host | Operation |
|---|---|
| `jlcsearch.tscircuit.com` | JLCPCB part search |
| `easyeda.com` | Original supplier component, symbol and footprint API |
| `modules.easyeda.com` | Original supplier STEP/OBJ models |
| `modelcdn.tscircuit.com` | Supplier model delivery used by the native importer |
| `registry-api.tscircuit.com` | Exact reference package, CLI authorization and publication |
| `files.omc-stepperonline.com` | Original motor drawing and STEP |

Import into a fresh staging directory first; inspect package identity, all
physical pin numbers, exposed pad, mounting features and CAD origin/rotation.
Transfer validated imports to `imports/supplier/` without overwriting existing
user files. Keep dependency caches and credentials out of Git. Re-imports must
compare hashes and explicitly account for supplier-library changes.

Only publish a separate NEMA11 prototype package after the relevant source,
schematic, electrical, physical, CAM and assembly gates have executed on that
same board revision. The requirements milestone is not a fabricated board.
