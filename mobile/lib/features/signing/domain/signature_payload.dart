class SignaturePayload {
  const SignaturePayload({
    required this.documentSha256,
    required this.signatureValue,
  });

  final String documentSha256;
  final String signatureValue;
}
