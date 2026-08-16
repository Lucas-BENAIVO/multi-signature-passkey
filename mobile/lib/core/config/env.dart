import 'package:flutter/foundation.dart';

/// Configuration d'environnement (URL API Django).
class Env {
  const Env._();

  /// Chrome/web → localhost ; émulateur Android → 10.0.2.2
  static String get apiBaseUrl {
    const fromDefine = String.fromEnvironment('API_BASE_URL');
    if (fromDefine.isNotEmpty) {
      return fromDefine;
    }
    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api';
    }
    return 'http://10.0.2.2:8000/api';
  }
}
