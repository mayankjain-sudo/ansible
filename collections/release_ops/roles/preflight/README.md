# `preflight` role

Validates release inputs and target-host prerequisites without changing
deployment files. Requires Ansible Core 2.18 or newer and Linux facts.

## Usage

For a deployment, supply the application, version, base directory, and
target-host archive:

```yaml
---
- name: Validate deployment prerequisites
  hosts: application_servers
  become: true
  roles:
    - role: mayankjain_sudo.release_ops.preflight
      vars:
        release_app_name: your-app
        release_version: "{{ app_version }}"
        release_base_dir: /opt/apps/your-app
        release_artifact_path: "{{ artifact_path }}"
```

The role defaults `release_preflight_operation` to `deploy`. For standalone
validation of rollback prerequisites, set it to `rollback`; the collection's
[`rollback` role](../rollback/README.md) sets this when it includes preflight.
The `release` and `deploy` roles also include preflight automatically, so
most playbooks should use one of those instead.

## Validation

For deployment, preflight checks the application and version naming rules,
absolute paths, Linux platform, artifact format and readability, and an
optional SHA-256 checksum. It also validates configured service and health
settings, ownership values, health-check limits, and that the releases,
current, and shared paths are safe, non-overlapping descendants of the
application base directory.

The archive must be readable on the managed host. Supported formats are
`.tar.gz` and `.zip`; `auto` format detection uses these suffixes. This role
does not inspect archive contents, create directories, extract files, or
change the active symlink.

For rollback operation, archive and deployment-version checks are skipped;
Linux, filesystem, ownership, service, and health-check configuration checks
still apply.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `release_preflight_operation` | `deploy` | `deploy` or `rollback`. |
| `release_app_name` | required | Safe application identifier. |
| `release_version` | required for deploy | Safe version directory name. |
| `release_base_dir` | required | Absolute, non-root application directory. |
| `release_artifact_path` | required for deploy | Absolute path to the target-host archive. |
| `release_artifact_format` | `auto` | `auto`, `tar.gz`, or `zip`. |
| `release_artifact_sha256` | empty | Optional expected 64-character SHA-256 digest. |
| `release_releases_dir` | `{{ release_base_dir }}/releases` | Versioned-release directory. |
| `release_current_path` | `{{ release_base_dir }}/current` | Active symlink. |
| `release_shared_dir` | `{{ release_base_dir }}/shared` | Shared-data directory. |

Additional validation uses the service and health-check variables documented
in the collection [configuration guide](../../docs/configuration.md).
