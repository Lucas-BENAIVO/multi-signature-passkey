class DocumentItem {
  const DocumentItem({
    required this.id,
    required this.title,
    required this.sha256,
    required this.status,
  });

  final int id;
  final String title;
  final String sha256;
  final String status;
}
