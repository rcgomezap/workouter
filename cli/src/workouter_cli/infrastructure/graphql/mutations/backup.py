"""Backup GraphQL mutations."""

TRIGGER_BACKUP = """
mutation TriggerBackup {
  triggerBackup {
    success
    filename
    sizeBytes
    createdAt
  }
}
"""
