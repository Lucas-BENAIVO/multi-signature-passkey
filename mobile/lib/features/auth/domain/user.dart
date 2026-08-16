class AppUser {
  const AppUser({
    required this.id,
    required this.username,
    required this.hasRsaPublicKey,
    this.email = '',
  });

  final int id;
  final String username;
  final String email;
  final bool hasRsaPublicKey;

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as int,
      username: json['username'] as String,
      email: (json['email'] as String?) ?? '',
      hasRsaPublicKey: json['has_rsa_public_key'] as bool? ?? false,
    );
  }
}
