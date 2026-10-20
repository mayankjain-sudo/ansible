# `rollback` role

Switches the active symlink to a retained release, applies configured service
management, verifies health, and attempts recovery to the release that was
active before the rollback if the requested target fails. Requires Ansible
Core 2.18 or newer and a Linux managed host.

## Usage

```yaml
---
- name: Roll back an application release
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.rollback
      vars:
        release_app_name: your-app
        release_base_dir: /opt/apps/your-app
        release_rollback_target_version: "1.4.1"
        release_manage_service: true
        release_service_name: your-app
        release_healthcheck_url: http://127.0.0.1:8080/health
```

If `release_rollback_target_version` is empty, the role uses the version
recorded in `<release_base_dir>/.release_ops_previous` by a successful
deployment or rollback. An explicit target must be a retained release
directory under the configured releases directory and must differ from the
active version.

## Behavior and results

Before changing the active pointer, the role runs shared preflight validation,
requires the application and releases paths to be real directories, checks
that the active symlink points directly to a retained release, and verifies
that the selected target exists. It then activates the target, applies the
configured service action if the pointer changed, and runs the health check.

On success, the previous active version is recorded for a future rollback and
`release_result` is set with `outcome: rollback_succeeded`. If activation,
service management, or health verification fails, the role attempts to
restore and verify the previously active release. The task still fails, with
`release_result` recording either `rollback_failed` (target failed but prior
release was recovered) or `recovery_failed` (recovery also failed). Original
and recovery errors are retained separately.

## Main variables

| Variable | Default | Description |
| --- | --- | --- |
| `release_app_name` | required | Application identifier. |
| `release_base_dir` | required | Absolute, non-root application directory. |
| `release_releases_dir` | `{{ release_base_dir }}/releases` | Versioned-release directory. |
| `release_current_path` | `{{ release_base_dir }}/current` | Active symlink. |
| `release_rollback_target_version` | empty | Explicit target; empty selects the recorded previous version. |
| `release_manage_service` | `false` | Whether to apply the configured service action. |
| `release_service_name` | empty | Required when service management is enabled. |
| `release_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `release_healthcheck_enabled` | `true` | Whether to verify the rollback target and recovery. |
| `release_healthcheck_url` | empty | Required when health checks are enabled. |
| `release_run_as_user` / `release_run_as_group` | `root` / `root` | Ownership for the previous-version marker. |

See the collection [configuration guide](../../docs/configuration.md) for
health-check limits and path constraints. Rollback does not transfer artifacts,
re-extract releases, or reverse database and other external side effects.
