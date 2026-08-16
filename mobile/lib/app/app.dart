import 'package:flutter/material.dart';
import 'package:multi_signature_passkey/app/theme.dart';

class MultiSignatureApp extends StatelessWidget {
  const MultiSignatureApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Multi Signature Passkey',
      theme: AppTheme.light,
      home: const Scaffold(
        body: Center(
          child: Text('Structure mobile prête'),
        ),
      ),
    );
  }
}
