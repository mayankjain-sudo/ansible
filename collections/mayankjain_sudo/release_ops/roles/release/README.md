# `release` role

Orchestrates a complete deployment: preflight validation, staged activation,
health verification, automatic recovery when configured, and structured
result reporting. Requires Ansible Core 2.18 or newer and a Linux managed
host.

## Usage

```yaml
---
- name: Deploy an application release
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.release
      vars:
        release_app_name: your-app
        release_version: "{{ app_version }}"
        release_base_dir: /opt/apps/your-app
        release_artifact_path: "{{ artifact_path }}"
        release_manage_service: true
        release_service_name: your-app
        release_healthcheck_url: http://127.0.0.1:8080/health
        release_auto_rollback: true
```

The archive must already be readable on each managed host; the role does not
transfer artifacts from the controller. Set the expected SHA-256 digest from
trusted build metadata when artifact verification is required.

## Workflow and results

The role validates inputs and the existing active release, stages and
publishes the requested immutable version, switches the active symlink,
applies the configured service action, and checks application health. On a
post-activation failure, it attempts to restore the prior release when
`release_auto_rollback` is enabled and a valid prior release exists. The
deployment remains failed even if recovery succeeds; the original deployment
error and recovery outcome are reported rather than hidden.

On success, the role stores the prior version in
`<release_base_dir>/.release_ops_previous` for later explicit rollback. The
host-level `release_result` fact reports the requested, previous, and active
versions, deployment outcome, rollback status, health-check status, and
recovery details. No release pruning is performed.

## Main variables

| Variable | Default | Description |
| --- | --- | --- |
| `release_app_name` | required | Application identifier. |
| `release_version` | required | Safe version directory name. |
| `release_base_dir` | required | Absolute, non-root application directory. |
| `release_artifact_path` | required | Absolute path to a readable archive on the managed host. |
| `release_releases_dir` | `{{ release_base_dir }}/releases` | Versioned-release directory. |
| `release_current_path` | `{{ release_base_dir }}/current` | Active symlink. |
| `release_shared_dir` | `{{ release_base_dir }}/shared` | Shared-data directory; not automatically mounted into releases. |
| `release_artifact_format` | `auto` | `auto`, `tar.gz`, or `zip`. |
| `release_artifact_sha256` | empty | Optional expected SHA-256 digest. |
| `release_auto_rollback` | `true` | Attempt recovery after a failure following activation. |
| `release_manage_service` | `false` | Apply the configured service action after activation/recovery. |
| `release_service_name` | empty | Required when service management is enabled. |
| `release_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `release_healthcheck_enabled` | `true` | Whether to check the application endpoint. |
| `release_healthcheck_url` | empty | Required when health checks are enabled. |

See the collection [configuration guide](../../docs/configuration.md) for all
variables and limits, and the [architecture guide](../../docs/architecture.md)
for filesystem and recovery behavior. Jobs modifying the same application
must be serialized across controllers; `serial: 1` only sequences hosts in
this play.
