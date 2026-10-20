# `deploy` role

Stages a target-host archive as an immutable, versioned release and switches
the application's `current` symlink to it. Requires Ansible Core 2.18 or
newer and a Linux managed host.

## Usage

```yaml
---
- name: Stage and activate a release
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.deploy
      vars:
        release_app_name: your-app
        release_version: "{{ app_version }}"
        release_base_dir: /opt/apps/your-app
        release_artifact_path: "{{ artifact_path }}"
        release_manage_service: true
        release_service_name: your-app
```

The archive must already exist and be readable on each managed host; this role
does not transfer it from the controller. Supported formats are `.tar.gz` and
`.zip` (`unzip` is required for ZIP extraction). Set
`release_artifact_sha256` to an independently trusted digest to verify the
artifact before staging.

## Behavior

The role includes `preflight` validation, creates the configured release
directories, and inspects archive paths and entry types before extraction. It
rejects unsafe or malformed archives and archives with no regular files.
Staging occurs in a unique temporary directory under the releases directory;
only a complete staged directory is published. An existing inactive version
is never overwritten. If the requested version is already active, it is not
re-extracted.

After publishing, the role points `current` at the requested version and
flushes the service handler if service management is enabled. It does not run
an HTTP health check or automatically restore a previous release on
post-activation failure. Use the [`release` role](../release/README.md) for
health verification and automatic recovery.

## Main variables

| Variable | Default | Description |
| --- | --- | --- |
| `release_app_name` | required | Application identifier used by preflight. |
| `release_version` | required | Safe version name for the release directory. |
| `release_base_dir` | required | Absolute, non-root application directory. |
| `release_releases_dir` | `{{ release_base_dir }}/releases` | Parent directory for versioned releases. |
| `release_current_path` | `{{ release_base_dir }}/current` | Active symlink path. |
| `release_shared_dir` | `{{ release_base_dir }}/shared` | Shared-data directory; contents are not mounted into releases. |
| `release_artifact_path` | required | Absolute path to the archive on the managed host. |
| `release_artifact_format` | `auto` | `auto`, `tar.gz`, or `zip`. |
| `release_artifact_sha256` | empty | Optional expected SHA-256 digest. |
| `release_run_as_user` / `release_run_as_group` | `root` / `root` | Ownership for directories and extracted content. |
| `release_manage_service` | `false` | Whether to run the configured service action after activation. |
| `release_service_name` | empty | Required when service management is enabled. |
| `release_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |

See the collection [configuration guide](../../docs/configuration.md) for
validation rules and all shared variables. Serialize jobs that modify the
same application; the role does not provide a cross-controller lock.
