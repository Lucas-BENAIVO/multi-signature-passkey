import 'package:flutter/foundation.dart';
import 'package:multi_signature_passkey/core/network/api_client.dart';
import 'package:multi_signature_passkey/core/storage/secure_storage.dart';
import 'package:multi_signature_passkey/features/auth/data/auth_api.dart';
import 'package:multi_signature_passkey/features/auth/domain/user.dart';

class AuthController extends ChangeNotifier {
  AuthController({
    required AuthApi authApi,
    required SecureStorageService storage,
  })  : _authApi = authApi,
        _storage = storage;

  final AuthApi _authApi;
  final SecureStorageService _storage;

  AppUser? user;
  bool isBootstrapping = true;
  bool isSubmitting = false;
  String? error;

  bool get isAuthenticated => user != null;

  Future<void> bootstrap() async {
    isBootstrapping = true;
    error = null;
    notifyListeners();

    try {
      final token = await _storage.readToken();
      if (token == null || token.isEmpty) {
        user = null;
        return;
      }
      user = await _authApi.me();
    } on ApiException {
      await _storage.clearToken();
      user = null;
    } catch (_) {
      await _storage.clearToken();
      user = null;
    } finally {
      isBootstrapping = false;
      notifyListeners();
    }
  }

  Future<bool> login({
    required String username,
    required String password,
  }) async {
    isSubmitting = true;
    error = null;
    notifyListeners();

    try {
      final result = await _authApi.login(
        username: username.trim(),
        password: password,
      );
      await _storage.saveToken(result.token);
      user = result.user;
      return true;
    } on ApiException catch (e) {
      error = e.message;
      user = null;
      return false;
    } catch (_) {
      error = 'Impossible de contacter le serveur. Vérifiez que Django tourne.';
      user = null;
      return false;
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _storage.clearToken();
    user = null;
    error = null;
    notifyListeners();
  }
}
