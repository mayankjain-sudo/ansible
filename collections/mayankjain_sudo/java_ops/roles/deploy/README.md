# `deploy` role

Safely inspects and extracts a downloaded ZIP or TAR.GZ archive into an
immutable, versioned release, then switches the `current` symlink. Requires
Ansible Core 2.16 or newer and a Linux managed host.

## Usage

Normally use the [`release` role](../release/README.md), which performs
preflight, download, deployment, health verification, and recovery. This role
expects the artifact download facts to be available; pair it with
[`download`](../download/README.md) when invoking it directly:

```yaml
---
- name: Download and deploy an application artifact
  hosts: java_servers
  become: true
  tasks:
    - name: Download the versioned artifact
      ansible.builtin.include_role:
        name: mayankjain_sudo.java_ops.download
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.zip"
        java_archive_artifact_path: target/orders-api.jar
        java_base_dir: /opt/apps/orders-api

    - name: Deploy the downloaded artifact
      ansible.builtin.include_role:
        name: mayankjain_sudo.java_ops.deploy
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_base_dir: /opt/apps/orders-api
```

The download step requires `java_artifact_url` to be the complete HTTP(S) URL
of the archive, including the repository host and path. The URL must end in
`.zip` or `.tar.gz`; the collection does not append a repository prefix.

## Behavior

The role inspects the archive and rejects absolute or traversal paths,
symlinks, hard links, unsupported entry types, and malformed data. It extracts
the archive into a unique staging directory beneath `java_releases_dir`,
verifies that `java_archive_artifact_path` exists as a regular file, and
creates a stable `<java_app_name>.<type>` link when the deployable is nested.
It publishes the complete directory as
`<java_releases_dir>/<java_app_version>`, then updates `java_current_path`.
An existing inactive version is not overwritten; use a new version for changed
content. An already active version is not re-staged.

For WAR deployments, `java_war_deploy_path` is linked to the WAR file in the
published release. The application server must support this symlink and must
be configured to monitor that path. If service management is enabled, the
role's handler applies the configured service action after activation.

Release pruning is disabled by default. Enable `java_prune_releases` only
after reviewing the recovery window and retention policy.

## Main variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required | Application name and artifact filename. |
| `java_app_version` | required | Immutable release directory name. |
| `java_artifact_type` | `jar` | Deployable type, `jar` or `war`. |
| `java_downloaded_artifact` | set by `download` | Cached archive path to extract. |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative JAR/WAR path inside the archive. |
| `java_base_dir` | required | Application root. |
| `java_releases_dir` | `{{ java_base_dir }}/releases` | Versioned release directory. |
| `java_current_path` | `{{ java_base_dir }}/current` | Active release symlink. |
| `java_war_deploy_path` | required for WAR | Application server deployment symlink path. |
| `java_manage_service` | `false` | Whether to apply service management after activation. |
| `java_service_name` | empty | Existing service name when service management is enabled. |
| `java_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `java_run_as_user` / `java_run_as_group` | `root` / `root` | Release file ownership. |
| `java_prune_releases` | `false` | Whether to remove older inactive releases. |
| `java_keep_releases` | `5` | Retention count when pruning is enabled. |

See the collection [configuration reference](../../docs/configuration.md) for
path constraints and all options.
