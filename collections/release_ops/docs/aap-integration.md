# Ansible Automation Platform integration

The collection has no AAP-only dependencies and can be used by local
`ansible-playbook`, CI, or an AAP Job Template.

1. Keep consumer playbooks in source control.
2. Build an execution environment with a tested `ansible-core` version and
   pin `mayankjain_sudo.release_ops` to a tested collection version.
3. Configure an AAP Project and Inventory for the target Linux hosts.
4. Create separate deployment and rollback Job Templates when their
   permissions or approval requirements differ.
5. Use surveys only for validated non-secret inputs, such as version and
   environment. Put credentials in AAP Credentials, not role defaults or
   survey fields.
6. Apply RBAC and approval workflows to production templates.
7. Grant the execution user the filesystem and service privileges required by
   the playbook; use `become` deliberately.
8. Capture `release_result` and task failure output for deployment audit and
   incident investigation.
9. Serialize deployments to a given application across all controllers;
   `serial: 1` only sequences hosts within one play execution.
10. Test the exact execution environment and AAP connectivity before
    production use.
11. Publish the expected artifact checksum as protected build metadata and
    pass it to `release_artifact_sha256`; do not calculate the expected value
    from the same untrusted artifact at deployment time.

An AAP deployment playbook can use the same role invocation shown in the
collection README. No AAP-specific lookup, API, or credential type is required
by the roles.
