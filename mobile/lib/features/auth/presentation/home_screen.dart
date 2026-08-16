import 'package:flutter/material.dart';
import 'package:multi_signature_passkey/features/auth/domain/user.dart';
import 'package:multi_signature_passkey/features/auth/presentation/auth_controller.dart';

/// Écran temporaire après login (liste documents à l'étape suivante).
class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.controller,
    required this.user,
  });

  final AuthController controller;
  final AppUser user;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace signataire'),
        actions: [
          IconButton(
            tooltip: 'Déconnexion',
            onPressed: controller.logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Connecté : ${user.username}',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                user.hasRsaPublicKey
                    ? 'Clé publique RSA enregistrée'
                    : 'Aucune clé publique RSA enregistrée',
              ),
              const SizedBox(height: 16),
              const Text('Prochaine étape : liste des documents.'),
            ],
          ),
        ),
      ),
    );
  }
}
