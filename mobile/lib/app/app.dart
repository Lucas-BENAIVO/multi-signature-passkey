import 'package:flutter/material.dart';
import 'package:multi_signature_passkey/app/theme.dart';
import 'package:multi_signature_passkey/core/config/env.dart';
import 'package:multi_signature_passkey/core/network/api_client.dart';
import 'package:multi_signature_passkey/core/storage/secure_storage.dart';
import 'package:multi_signature_passkey/features/auth/data/auth_api.dart';
import 'package:multi_signature_passkey/features/auth/presentation/auth_controller.dart';
import 'package:multi_signature_passkey/features/auth/presentation/home_screen.dart';
import 'package:multi_signature_passkey/features/auth/presentation/login_screen.dart';
import 'package:multi_signature_passkey/shared/widgets/app_loading.dart';

class MultiSignatureApp extends StatefulWidget {
  const MultiSignatureApp({super.key});

  @override
  State<MultiSignatureApp> createState() => _MultiSignatureAppState();
}

class _MultiSignatureAppState extends State<MultiSignatureApp> {
  late final SecureStorageService _storage;
  late final ApiClient _apiClient;
  late final AuthController _authController;

  @override
  void initState() {
    super.initState();
    _storage = SecureStorageService();
    _apiClient = ApiClient(
      baseUrl: Env.apiBaseUrl,
      getToken: _storage.readToken,
    );
    _authController = AuthController(
      authApi: AuthApi(_apiClient),
      storage: _storage,
    );
    _authController.bootstrap();
  }

  @override
  void dispose() {
    _authController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Multi Signature Passkey',
      theme: AppTheme.light,
      home: AnimatedBuilder(
        animation: _authController,
        builder: (context, _) {
          if (_authController.isBootstrapping) {
            return const Scaffold(body: AppLoading());
          }
          if (_authController.isAuthenticated) {
            return HomeScreen(
              controller: _authController,
              user: _authController.user!,
            );
          }
          return LoginScreen(controller: _authController);
        },
      ),
    );
  }
}
