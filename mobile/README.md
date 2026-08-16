# Mobile — multi-signature-passkey

Application Flutter (signataires) branchée sur l'API Django.

## Structure

```
lib/
  app/                 # bootstrap app, thème, navigation
  core/                # transversal : config, réseau, stockage, crypto
  features/            # par fonctionnalité (auth, documents, signing)
    */data/            # API / sources
    */domain/          # modèles / règles
    */presentation/    # écrans / widgets
  shared/              # widgets réutilisables
```

## Prérequis

1. Installer Flutter : https://docs.flutter.dev/get-started/install
2. Depuis ce dossier :

```bash
cd mobile
flutter create . --project-name multi_signature_passkey
flutter pub get
```

`flutter create .` génère `android/`, `ios/`, etc. sans écraser `lib/`.
