# `release` role

Orchestrates the complete Java deployment workflow: input validation,
repository download, versioned deployment, optional service management,
health verification, automatic recovery, and result reporting. Requires
Ansible Core 2.16 or newer on Linux.

## Usage

```yaml
---
- name: Deploy an application release
  hosts: java_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.release
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.tar.gz"
        java_archive_artifact_path: app/orders-api.jar
        java_artifact_sha256: "{{ artifact_sha256 }}"
        java_base_dir: /opt/apps/orders-api
        java_manage_service: true
        java_service_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
        java_artifact_username: "{{ vault_nexus_username }}"
        java_artifact_password: "{{ vault_nexus_password }}"
```

Set `java_artifact_url` to the complete HTTP(S) URL for the ZIP or TAR.GZ
archive. Set `java_archive_artifact_path` to the JAR or WAR path relative to
the archive root (default: `<app name>.<type>`).

For WARs, set `java_artifact_type: war` and provide
`java_war_deploy_path`, the dedicated WAR path monitored by the application
server. The server must support the managed symlink. This role does not
install a service definition or configure a specific server.

## Workflow and results

The role runs preflight, downloads the artifact on the managed host, stages
and activates its immutable release directory, then performs service and
health actions. If a failure occurs after activation, it attempts to restore
the previous version when `java_auto_rollback` is enabled and a retained prior
release exists. A failed deployment remains a failed Ansible job even when
recovery succeeds.

Successful deployments record the prior version in
`<java_base_dir>/.java_ops_previous` for later rollback. A host-level
`java_result` fact records versions, deployment outcome, health-check status,
and rollback/recovery status.

## Frequently used variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required | Application identifier. |
| `java_app_version` | required | Safe release version. |
| `java_artifact_type` | `jar` | `jar` or `war`. |
| `java_artifact_url` | required | Complete HTTP(S) URL ending in `.zip` or `.tar.gz`. |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative deployable path within the archive. |
| `java_artifact_sha256` | empty | Optional expected SHA-256 digest. |
| `java_artifact_username` / `java_artifact_password` | empty | Optional Basic auth credentials. |
| `java_artifact_bearer_token` | empty | Optional token; mutually exclusive with Basic auth. |
| `java_base_dir` | required | Absolute, non-root application directory. |
| `java_war_deploy_path` | required for WAR | Application server's WAR symlink path. |
| `java_manage_service` | `false` | Whether to manage an existing service. |
| `java_service_name` | empty | Required if service management is enabled. |
| `java_healthcheck_enabled` | `true` | Whether to verify the health endpoint. |
| `java_healthcheck_url` | empty | Required when health checks are enabled. |
| `java_auto_rollback` | `true` | Attempt recovery after post-activation failure. |
| `java_prune_releases` | `false` | Enable removal of older inactive versions. |

See the collection [configuration reference](../../docs/configuration.md) and
[deployment guide](../../docs/deployment-guide.md) for all variables, JAR/WAR
examples, retention, and operational guidance. Serialize jobs that modify
the same application across all controllers.
