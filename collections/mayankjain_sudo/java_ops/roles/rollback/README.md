# `rollback` role

Activates a previously deployed Java release, applies optional service
management, and verifies application health. If activation or verification
fails, it attempts to restore the version that was active before rollback.
Requires Ansible Core 2.16 or newer and a Linux host.

## Usage

```yaml
---
- name: Roll back an application release
  hosts: java_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.rollback
      vars:
        java_app_name: orders-api
        java_base_dir: /opt/apps/orders-api
        java_rollback_target_version: "3.8.0"
        java_manage_service: true
        java_service_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
```

When `java_rollback_target_version` is empty, the role reads the previously
recorded version from `<java_base_dir>/.java_ops_previous`. The selected
version must be a retained release directory under `java_releases_dir` and
must differ from the current version.

## Behavior and result

Before activation, the role runs preflight, verifies the active pointer and
selected release, and requires the current release to remain available for
recovery. It then switches the `current` symlink, updates the WAR symlink when
`java_artifact_type: war`, applies the configured service action, and runs the
health check.

On success, the former current version is recorded for a later rollback and
the `java_result` fact reports `rollback_succeeded`. If the target fails but
the former version is restored and healthy, the role still fails and reports
`rollback_failed`. If recovery also fails, it reports `recovery_failed`.

For WAR rollback, pass the same `java_artifact_type: war` and
`java_war_deploy_path` settings used for deployment. The WAR archive's
configured `java_archive_artifact_path` is published under the stable
`<java_app_name>.war` name in each release. Configure and test the application
server's symlink handling separately.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required | Application identifier. |
| `java_base_dir` | required | Absolute application directory. |
| `java_releases_dir` | `{{ java_base_dir }}/releases` | Directory containing retained versions. |
| `java_current_path` | `{{ java_base_dir }}/current` | Active release symlink. |
| `java_rollback_target_version` | empty | Explicit target; empty selects the recorded previous version. |
| `java_artifact_type` | `jar` | `jar` or `war`. |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative deployable path inside downloaded archives. |
| `java_war_deploy_path` | required for WAR | Application server's WAR deployment symlink path. |
| `java_manage_service` | `false` | Whether to apply service management. |
| `java_service_name` | empty | Required when service management is enabled. |
| `java_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `java_healthcheck_enabled` | `true` | Whether to verify the target and recovery. |
| `java_healthcheck_url` | empty | Required when health checks are enabled. |

See the collection [configuration reference](../../docs/configuration.md) for
health-check limits, path requirements, and all shared variables.
