# Configuration

All public variables use the `release_` prefix. The `release` role runs
`preflight`, `deploy`, `healthcheck`, and recovery in that order.

| Variable | Default | Description |
| --- | --- | --- |
| `release_app_name` | required | Application identifier; letters, numbers, `_`, `.`, and `-`. |
| `release_version` | required for deploy | Release directory name; conservative alphanumeric/dot/underscore/plus/hyphen form; `..` is rejected. |
| `release_base_dir` | required | Absolute application root. |
| `release_releases_dir` | `{{ release_base_dir }}/releases` | Versioned release directory. |
| `release_current_path` | `{{ release_base_dir }}/current` | Active symlink. |
| `release_shared_dir` | `{{ release_base_dir }}/shared` | Mutable/shared-data location; not mounted automatically. |
| `release_artifact_path` | required for deploy | Absolute path to a target-host archive. |
| `release_artifact_format` | `auto` | `auto`, `tar.gz`, or `zip`; `auto` uses the file suffix. |
| `release_artifact_sha256` | empty | Optional expected SHA-256 digest. |
| `release_run_as_user` | `root` | Owner assigned to directories and extracted content. |
| `release_run_as_group` | `root` | Group assigned to directories and extracted content. |
| `release_auto_rollback` | `true` | Attempt recovery after a post-activation failure. |
| `release_rollback_target_version` | empty | Explicit rollback target; empty selects the recorded previous version. |
| `release_manage_service` | `false` | Enable service restart/reload. When true, service name is required. |
| `release_service_name` | empty | Service managed by `ansible.builtin.service`. |
| `release_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `release_healthcheck_enabled` | `true` | Disable only when the application has no HTTP(S) health endpoint. |
| `release_healthcheck_url` | empty | Required when health checks are enabled. |
| `release_expected_status` | `200` | Expected HTTP status in the 100-599 range. |
| `release_healthcheck_retries` | `10` | Number of endpoint attempts; must be positive. |
| `release_healthcheck_delay` | `3` | Seconds between attempts; must be non-negative. |
| `release_healthcheck_timeout` | `5` | Per-request timeout in seconds; must be positive. |
| `release_keep_releases` | `5` | Reserved; cleanup is not implemented and no releases are pruned. |

The base directory must be an absolute, non-root path. The releases directory,
current symlink path, and shared directory must be descendants of the base
directory and must not overlap one another. Configured paths cannot contain
`.` or `..` components. These constraints protect both deployment staging and
rollback from ambiguous or overlapping filesystem destinations.

Both deployment and rollback run shared preflight validation before changing
the active pointer. Rollback skips only artifact- and deployment-version
checks; it still validates Linux, application identity, filesystem paths,
service configuration, health-check configuration and limits, and ownership
settings. An enabled health check therefore requires a non-empty
`release_healthcheck_url` before rollback can start.

Example explicit rollback:

```yaml
---
- name: Restore a release
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.rollback
      vars:
        release_app_name: payments-api
        release_base_dir: /opt/apps/payments-api
        release_rollback_target_version: "1.4.1"
        release_manage_service: true
        release_service_name: payments-api
        release_healthcheck_url: http://127.0.0.1:8080/health
```

If the explicit target is omitted, the rollback role reads
`<release_base_dir>/.release_ops_previous`, written only after a successful
deployment. Rollback verifies the target directory before changing the active
link, and validates that the active release is retained so it can be restored
if the requested rollback fails. It then applies configured service management
and health verification. A healthy target reports `rollback_succeeded`. If the
target fails but the prior release is restored and healthy, the role reports
`rollback_failed`; if restoring or verifying the prior release fails, it
reports `recovery_failed`. In either failure result, `rollback_error` preserves
the original failure and `recovery_error` preserves any recovery failure.

The orchestrator leaves `release_result` available as an Ansible fact:

```yaml
release_result:
  app_name: payments-api
  requested_version: "1.0.1"
  previous_version: "1.0.0"
  active_version: "1.0.1"
  deployment_status: deployment_succeeded
  outcome: deployment_succeeded
  rollback_status: not_required
  healthcheck_status: healthy
  recovery_required: false
```
