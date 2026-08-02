# Flutter Architecture Best Practices

This document contains standard patterns for the Wrfcoin mobile app.

## Project Structure

```
lib/
├── core/
│   ├── theme/
│   ├── network/
│   ├── utils/
│   └── constants/
├── features/
│   └── [feature_name]/
│       ├── domain/
│       │   ├── models/
│       │   └── repositories/
│       ├── data/
│       │   ├── data_sources/
│       │   └── repositories_impl/
│       └── presentation/
│           ├── pages/
│           ├── widgets/
│           └── controllers/ (Riverpod Notifiers)
└── services/
    ├── FFI/
    └── push_notifications/
```

## State Management Pattern (Riverpod)

Always prefer `AsyncNotifier` for state that requires asynchronous fetching.

```dart
// BAD: Manual loading state
class WeatherState {
  final bool isLoading;
  final WeatherData? data;
}

// GOOD: Riverpod AsyncValue
@riverpod
class WeatherForecast extends _$WeatherForecast {
  @override
  Future<WeatherData> build() async {
    return ref.watch(weatherRepositoryProvider).getForecast();
  }
}
```
