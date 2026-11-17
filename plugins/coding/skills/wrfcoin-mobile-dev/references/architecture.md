# WRFCoin mobile: module map

Snapshot of `wrfcoin/mobile` `lib/` on main, 2026-11-17 (0.1.3+6). Re-list with
`git ls-tree -r --name-only origin/main lib` when in doubt.

## Top level

```
lib/
├── main.dart, app.dart        entry point and app widget
├── bootstrap/                 app_overrides.dart (provider overrides at start-up)
├── core/                      auth handoff, api_constants, errors, feature flags,
│                              formatting, layout, localization, network (public reads),
│                              preferences, routing (go_router), theme, time, widgets
├── features/<name>/           data/ (models, repositories), domain/, presentation/
│                              (providers, screens, widgets)
└── services/                  api, auth, background, crypto, location,
                               notifications, observability, offline, pws,
                               referral, security, storage
```

## services/crypto

| File | Role |
|---|---|
| key_manager.dart | Biometric-gated wallet seed; the only wallet signer |
| wallet_secure_storage.dart | Keystore/Keychain-backed key-value store |
| wallet_setup_service.dart | Create/import flows |
| wallet_vault.dart | Multi-wallet store (flag `enableMultiWallet`, default off); station wallet not removable |
| collect_key_store.dart | Unprompted per-phone collect key; signs only own-station commit authorizations |
| station_signing.dart | Station registration (v2, includes collect pubkey) and owner-action preimages |
| commit_id.dart | Commit identifiers for collect submissions |
| signed_transfer.dart, transparent_transfer_authorization.dart | Transfer preimages and signatures |
| transfer_signing_domain.dart | Chain/network identity (`WRFCOIN_CHAIN_ID`, `WRFCOIN_NETWORK_ID`) |
| ed25519_wallet_login.dart | Validates the backend login challenge before signing |
| advisory_action_signing.dart | Chain 888 advisory vote/propose; u64-LE length framing; core4 vectors |
| governance_vote_signing.dart | Legacy v1 vote bytes, `WRFCOIN_GOVERNANCE_SIGNING_VERSION` |
| foreground_after_unlock.dart | Waits for `resumed` after a device unlock before signing |

## features

| Feature | What a person does there |
|---|---|
| wallet | Create/import, recovery phrase, send, receive, address book, send allowlist, passkey wallet, emergency wipe, reward totals |
| governance | Proposal list/detail, vote, advisory propose, treasury |
| network_nodes | Ladder view: producers, bonded nodes, attesters (`/api/network/nodes`) |
| explorer | Chain view (`/wallet/chain`) |
| faucet | Testnet faucet request |
| collector | Phone-as-a-station: sensors, registration, recovery/transfer, field mode |
| weather | Current, forecast, map, alerts |
| onboarding | Welcome flow and tour |
| gamification, challenges, duels, competitions, communities, carbon_lottery | Leaderboards and games (several dark-launched) |
| forecast_check, sky_view, calibration, field_diagnostics, sdr_apt, analytics | Forecast and sensor tools |
| notifications, settings, more, social, wear, widgets | Shell and platform extras |

## Patterns

- Riverpod 3 providers in `presentation/providers/`; repositories in `data/repositories/`.
- Errors map through `core/errors/dio_error_mapper.dart`; show `AppErrorWidget`, never a
  fake value when a read fails.
- Feature flags: `core/feature_flags/feature_flags.dart` (runtime, persisted) and
  `build_flags.dart` (compile-time `--dart-define`).
