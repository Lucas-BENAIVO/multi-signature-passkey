class AppUser {
  const AppUser({
    required this.id,
    required this.username,
    required this.hasRsaPublicKey,
  });

  final int id;
  final String username;
  final bool hasRsaPublicKey;
}
