---
name: wrfcoin-mobile-dev
description: Specialized context and instructions for developing the Wrfcoin mobile app using Flutter and Dart. Use this skill when asked to create, modify, or debug features within the 'wrfcoin/mobile' repository, specifically dealing with the blockchain wallet, background sensor data collection (barometer/GPS), environmental forecasting UI, or communicating with the Wrfcoin backend and core Rust modules via FFI or gRPC.
---

# Wrfcoin Mobile Development Guide

This skill provides the necessary context and technical constraints for working on the Wrfcoin Flutter application.

## Core Architecture

The mobile app follows a Feature-Driven Architecture. Always place new code in the appropriate feature module under `lib/features/` rather than dumping everything in the root or a generic `components/` folder.

- **`lib/features/wallet/`**: Blockchain key management, stealth addresses, transaction signing.
- **`lib/features/collector/`**: Smartphone-as-a-sensor logic (background GPS, barometer reading, local SQLite/Hive caching).
- **`lib/features/weather/`**: UI for displaying hyper-local environmental forecasts and AR data overlays.
- **`lib/features/governance/`**: Interactions with the Wrfcoin AI-DAO.

## Key Constraints & Standards

1. **Security First (Wallet/Keys):** 
   - Never log or expose mnemonic phrases, private keys, or raw `0x` addresses in plaintext. 
   - Always use secure enclave storage (via `flutter_secure_storage`) for keys. 
   - Mask addresses in the UI and logging.

2. **Data Collection (Smartphone-as-a-Sensor):**
   - Background tasks must be battery-optimized. Do not run continuous GPS polling.
   - Use movement-triggered geofencing or 15-minute interval wakeups to sample barometer/temperature data.
   - All collected data must be queued to a local offline database (SQLite/Hive) and synced only when an active network connection is available to prevent data loss in dead zones.

3. **State Management:**
   - Use Riverpod for global state management and dependency injection.
   - Maintain a clear separation between the UI (Widgets) and Business Logic (Providers/Notifiers).

4. **Integration with Wrfcoin Core:**
   - Cryptographic heavy lifting (like Zero-Knowledge proofs and Stealth Address generation) should not be written in raw Dart.
   - Interfaces should eventually map to Rust FFI bindings from the `blockchain-core` or make secure gRPC calls to the backend.

## Common Development Workflows

When implementing a new feature, follow this flow:
1. Define the Data Model (`.model.dart`)
2. Build the Repository/Service layer for API or local database interactions.
3. Create the Riverpod Notifier to manage the feature's state.
4. Build the UI Widgets in the feature's `presentation/` folder.
