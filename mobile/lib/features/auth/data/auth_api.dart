import 'package:multi_signature_passkey/core/network/api_client.dart';
import 'package:multi_signature_passkey/features/auth/domain/user.dart';

class AuthApi {
  AuthApi(this._client);

  final ApiClient _client;

  Future<({String token, AppUser user})> login({
    required String username,
    required String password,
  }) async {
    final data = await _client.postJson(
      '/auth/login/',
      body: {
        'username': username,
        'password': password,
      },
      auth: false,
    );

    final token = data['token'] as String?;
    final userJson = data['user'] as Map<String, dynamic>?;
    if (token == null || userJson == null) {
      throw ApiException('Réponse login invalide.');
    }

    return (token: token, user: AppUser.fromJson(userJson));
  }

  Future<AppUser> me() async {
    final data = await _client.getJson('/auth/me/');
    return AppUser.fromJson(data);
  }
}
