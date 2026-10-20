# Architecture and safety

The collection supports Linux applications that can run from a versioned
directory and whose active version is selected by a symlink. It does not
assume applications support this filesystem model.

Deployment proceeds in this order:

1. Preflight validates inputs, Linux facts, artifact readability, archive
   format, and optional checksum. No deployment paths are changed.
2. A unique staging directory is created below the releases directory.
3. Archive entries are inspected for absolute paths, `..` traversal, and
   entry types before extraction. Symbolic links, hard links, and other
   non-file/non-directory types are rejected. Malformed archives and archives
   with corrupt member data are rejected; an empty archive is also rejected.
4. Staging is renamed into the final version directory. Existing inactive
   release directories are never overwritten.
5. The active symlink is switched to the complete release. The previous
   symlink target is retained in memory for recovery.
6. The configured service action runs and HTTP health verification is retried.
7. On post-activation failure, the previous symlink is restored when enabled
   and available, and service/health verification is repeated. The original
   deployment failure remains fatal even after successful recovery.

After successful deployment, the previous version is stored in
`.release_ops_previous` for a later explicit `rollback` role invocation. Failed
releases are retained for investigation. No automatic release pruning occurs.

## Operational constraints

- Artifacts must be trusted and produced by a controlled build pipeline.
  Archive inspection is defense in depth, not a substitute for artifact
  provenance or isolation.
- The archive must be staged on the target host. Transfer and artifact
  provenance are responsibilities of the calling playbook/pipeline.
- A checksum detects artifact mismatch only when the expected digest comes
  from a trusted source independent of the artifact, such as signed build
  metadata or a protected pipeline variable.
- Concurrent jobs for the same application are not locked. Serialize jobs
  across all controllers that can modify the host.
- Service and HTTP health checks are application-specific; this collection
  does not reverse database migrations or external side effects.
- Check mode does not simulate extraction, service availability, pointer
  replacement, or health behavior.
- The symlink update uses `ansible.builtin.file`; atomic replacement is
  filesystem and Ansible-version dependent.
