---
name: wrfcoin-mobile-dev
version: 2.0.0
last-updated: 2026-11-17
description: >-
  Working guide for the WRFCoin phone app (Flutter/Dart, public repo
  wrfcoin/mobile, chain 888 testnet). Use when creating, changing, testing,
  building or installing the app: wallets and the multi-wallet vault, send and
  receive, phone-as-a-station collect key, advisory governance vote/propose
  signing, the node ladder screen, API and chain --dart-define flags, profile
  or release APK builds, the flutter test file-list workaround, and wireless
  adb installs on the owner's phone.
---

# WRFCoin mobile app

The app is a Flutter client for the chain 888 public testnet: wallets, sends, a
phone weather station, advisory governance and read-only network views. Keys
stay on the phone; the app signs and the backend relays. There is **no Rust FFI**
and nothing in it comes from the frozen `blockchain-core` repo. Signing is pure
Dart (`cryptography`, `pointycastle`), pinned byte-for-byte to core4 / backend
golden vectors.

## Where to work

- Code: a worktree off `/home/tony/wrfcoin-public/mobile` (origin `wrfcoin/mobile`),
  branched from `origin/main`. `/home/tony/wrfcoin/mobile` is the read-only archive
  clone: never branch or open PRs there.
- Before `gh pr create`: print `pwd` and `git remote get-url origin`; it must be
  `wrfcoin/mobile`.
- Version: read `version:` in `pubspec.yaml` (0.1.3+6 on main at 2026-11-17; the
  owner's phone ran 0.1.3+5). Every public APK needs a higher build number (`+N`)
  than the last one, or Android refuses the update.
- Old issue and PR numbers in comments (`mobile#…`, `backend#…`, `core4#…`) point
  at the private `*-archive` repos, not the public ones.

## Module map

Full list with file names: [references/architecture.md](references/architecture.md).

- `lib/services/crypto/`: all key handling and signing.
  - `key_manager.dart`, `wallet_secure_storage.dart`, `wallet_setup_service.dart`:
    the biometric-gated ed25519 wallet seed (Keystore/Keychain).
  - `wallet_vault.dart`: multi-wallet store, dark-launched behind
    `FeatureFlags.enableMultiWallet` (default off). The station wallet is bound to
    the station and cannot be removed (owner ruling 2026-10-28).
  - `collect_key_store.dart`: a second, unprompted ed25519 "collect key" that only
    signs commit authorizations for this phone's own station (background worker).
  - `station_signing.dart`: station registration and owner-action preimages.
  - `signed_transfer.dart`, `transfer_signing_domain.dart`,
    `transparent_transfer_authorization.dart`: sends.
  - `ed25519_wallet_login.dart`: checks the backend's login challenge (origin, chain,
    network, expiry) before signing it.
  - `advisory_action_signing.dart`: advisory governance (vote and propose) for chain
    888, byte-identical to core4 `advisory_action_message` and the website's
    `advisoryActionMessage`; vectors in
    `test/services/crypto/advisory_governance_vectors.json`. Proposals cost a 1 WRF
    deposit; the relay builds the transaction with fee 0.
  - `governance_vote_signing.dart`: the older v1 vote bytes
    (`governance-vote-v1|id|approve`), version via
    `WRFCOIN_GOVERNANCE_SIGNING_VERSION`.
  - `foreground_after_unlock.dart`: waits briefly after the device unlock for the
    app to be `resumed` again, so signing happens only on screen.
- `lib/features/wallet/`: create/import, recovery phrase, send/receive, address book,
  send allowlist, passkey wallet (a web page creates and signs for it), emergency
  wipe, balance card, rewards.
- `lib/features/governance/`: proposal list/detail, vote screen, advisory propose
  screen and vote panel, treasury card.
- `lib/features/network_nodes/`: the ladder view (`/wallet/nodes`), read-only from
  `GET /api/network/nodes`: producers, bonded nodes, attesters.
- `lib/features/collector/` + `lib/services/background/`: phone-as-a-station
  sensors, Workmanager sync and collection service.
- Other features: weather, explorer (`/wallet/chain`), faucet, onboarding/welcome,
  gamification, challenges, duels, competitions, forecast_check, sky_view,
  calibration, field_diagnostics, notifications, settings. Several are dark-launched
  in `lib/core/feature_flags/feature_flags.dart`.
- YubiKey: the phone app has no YubiKey code yet. YubiKey-required wallets are a
  ladder/web topic; don't claim phone support.
- State is Riverpod 3 (`flutter_riverpod`), routing is `go_router`
  (`lib/core/routing/app_router.dart`), HTTP is `dio` with CA-root TLS pinning in
  release builds.

## Build flags (`--dart-define`)

| Define | Public testnet value | Notes |
|---|---|---|
| `API_BASE_URL` | `https://wrfcoin.com/api` | Debug default is `http://localhost:4001/api`; release refuses placeholders and empty values. |
| `WRFCOIN_WALLET_AUTH_ORIGIN` | **leave unset** | The app derives `https://wrfcoin.com` from the API URL, which is what the live login challenge names. An old tailnet origin breaks every login. Re-check the live challenge's `URI:` line before each build. |
| `WRFCOIN_CHAIN_ID` | `888` | Required for profile and release builds (compile fails without it). |
| `WRFCOIN_NETWORK_ID` | `testnet` (default) | |
| `TLS_PIN_SET` | `cloudflare-universal-v1` | Release builds only. |
| `WRFCOIN_WALLET_SEND` | `on` / `off` | Profile tester builds hide Send unless `on`. |

## Test

Checks from CONTRIBUTING: `flutter analyze --no-pub`, tests, `flutter build apk --debug`.

On the workstation a bare `flutter test` hangs for an hour or more on two files that
bind local sockets: `test/integration/testnet_smoke_probe_test.dart` and
`test/services/api/certificate_pinning_test.dart`. Run an explicit list instead:

```bash
find test -name '*_test.dart' \
  ! -path test/integration/testnet_smoke_probe_test.dart \
  ! -path test/services/api/certificate_pinning_test.dart \
  | sort | xargs flutter test --no-pub --concurrency=2
```

About 5–8 minutes. Say in the PR that CI covers those two files (CI runs the full
suite on hosted runners). Stop a stuck run by its exact PID, never by pattern.

## Build an APK

- Builds run in GitHub CI (`ci.yml` builds a debug APK; `mobile-release.yml` is the
  signed store pipeline), on the workstation, or on CT102. **Never build on a host
  that runs a live chain node** (Mango, the N5/CT101 producer).
- Tester APK (debug-signed, profile mode):
  `WRFCOIN_CHAIN_ID=888 scripts/build_profile_apk.sh https://wrfcoin.com/api`.
  It refuses a different signer or a debuggable APK. Tester APKs never upgrade the
  public one.
- The public `/downloads` APK is a release build made with the owner's release
  script and release key. Don't build or publish that one without the lead.
- Run `flutter clean` before a build that changes defines.

## Install on the owner's phone (wireless adb)

- `adb connect <phone-ip>:<connect-port>`. If that fails while the phone pings,
  re-pair: on the phone, Wireless debugging > Pair device with pairing code, then
  `adb pair <phone-ip>:<pair-port> <code>` and connect again. The pairing port is not
  the connect port.
- The APK is ~80 MB and Wi-Fi adb runs ~0.3 MB/s (4–5 minutes). Run it in the
  background with no short `timeout`.
- `adb install -r` on a file name with `+` fails. Push to a plain name, check, install,
  remove:

```bash
adb push wrfcoin-<version>.apk /data/local/tmp/wrfcoin.apk
adb shell sha256sum /data/local/tmp/wrfcoin.apk   # compare with the local sha256sum
adb shell pm install -r /data/local/tmp/wrfcoin.apk
adb shell rm /data/local/tmp/wrfcoin.apk
```

Uninstalling wipes the wallet (`allowBackup=false`), so always install over the top
with the same signer.

## Rules

- Never log, print or screenshot a recovery phrase, seed, private key or full
  address; the code masks addresses and redacts telemetry
  (`services/observability/telemetry_redactor.dart`).
- Signing code changes need matching golden vectors from core4/backend/frontend;
  never "fix" a vector to make a test pass.
- UI changes include a screenshot at phone and desktop width in the PR.
- Merge on green CI.
