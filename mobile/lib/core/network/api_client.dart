import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({
    required this.baseUrl,
    this.getToken,
  });

  final String baseUrl;
  final Future<String?> Function()? getToken;

  Uri _uri(String path) {
    final normalizedBase = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$normalizedBase$normalizedPath');
  }

  Future<Map<String, dynamic>> postJson(
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    final response = await http.post(
      _uri(path),
      headers: await _headers(auth: auth),
      body: body == null ? null : jsonEncode(body),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> getJson(String path) async {
    final response = await http.get(
      _uri(path),
      headers: await _headers(auth: true),
    );
    return _decode(response);
  }

  Future<Map<String, String>> _headers({bool json = true, bool auth = true}) async {
    final headers = <String, String>{};
    if (json) {
      headers['Content-Type'] = 'application/json';
      headers['Accept'] = 'application/json';
    }
    if (auth) {
      final token = getToken == null ? null : await getToken!();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Token $token';
      }
    }
    return headers;
  }

  Map<String, dynamic> _decode(http.Response response) {
    Map<String, dynamic> data = <String, dynamic>{};
    if (response.body.isNotEmpty) {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        data = decoded;
      } else {
        data = {'data': decoded};
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    }

    final detail = data['detail'] ?? data['non_field_errors'] ?? data;
    throw ApiException(
      detail.toString(),
      statusCode: response.statusCode,
    );
  }
}
