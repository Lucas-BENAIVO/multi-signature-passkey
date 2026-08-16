/// Configuration d'environnement (URL API Django, etc.).
class Env {
  const Env._();

  /// En émulateur Android : 10.0.2.2 pointe vers le localhost de la machine hôte.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',
  );
}
