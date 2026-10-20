# `preflight` role

Validates the Java deployment or rollback inputs and filesystem configuration
before other roles make changes. It requires Linux facts and Ansible Core 2.16
or newer.

## Usage

Most playbooks should use the [`release` role](../release/README.md) or
[`rollback` role](../rollback/README.md), which include preflight themselves.
Use this role directly when a pipeline needs an explicit validation step:

```yaml
---
- name: Validate Java deployment configuration
  hosts: java_servers
  become: true
  gather_facts: true
  roles:
    - role: mayankjain_sudo.java_ops.preflight
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.tar.gz"
        java_archive_artifact_path: app/orders-api.jar
        java_base_dir: /opt/apps/orders-api
```

The default `java_operation` is `deploy`. Set it to `rollback` to validate
rollback prerequisites without requiring a deployment version or artifact
URL.

## What it validates

- Application name, artifact type, and (for deployment) version and complete
  HTTP(S) artifact URL. The URL must contain no parent-directory components
  and end in `.zip` or `.tar.gz`.
- The relative JAR/WAR path inside the archive must be normalized and contain
  no parent-directory components.
- Linux platform, ownership, enabled service settings, and health-check
  configuration and limits.
- For WARs, an absolute deployment path without parent-directory components.
- Absolute, normalized, distinct release, current, and cache paths below the
  application base directory.
- Optional SHA-256 format and mutually exclusive HTTP Basic or bearer-token
  authentication configuration.

Preflight does not download artifacts, create directories, change symlinks,
manage services, or run health checks.

## Important variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_operation` | `deploy` | `deploy` or `rollback`. |
| `java_app_name` | required | Safe application identifier. |
| `java_app_version` | required for deploy | Safe release version. |
| `java_artifact_type` | `jar` | `jar` or `war`. |
| `java_artifact_url` | required for deploy | Complete HTTP(S) URL ending in `.zip` or `.tar.gz`. |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative JAR/WAR path in the archive. |
| `java_artifact_sha256` | empty | Optional 64-character SHA-256 digest. |
| `java_base_dir` | required | Absolute, non-root application directory. |
| `java_releases_dir` | `{{ java_base_dir }}/releases` | Release directory. |
| `java_current_path` | `{{ java_base_dir }}/current` | Active symlink path. |
| `java_artifact_cache_dir` | `{{ java_base_dir }}/cache` | Artifact cache. |
| `java_war_deploy_path` | required for WAR | Application server's WAR symlink path. |

Service, health-check, credentials, and ownership variables are also validated.
See the collection [configuration reference](../../docs/configuration.md) for
the complete list.
