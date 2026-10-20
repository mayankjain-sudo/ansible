# Ansible Collection - `mayankjain_sudo.java_ops`

Ansible roles for downloading ZIP/TAR.GZ bundles from a user-supplied artifact
URL and deploying their executable JAR or application-server WAR payloads as
versioned releases on Linux hosts.

The collection supports staged deployment, optional SHA-256 verification,
service management, HTTP(S) health checks, automatic recovery, explicit
rollback, and release retention. It does not create Java systemd unit files or
configure a specific application server. Configure the service and, for WARs,
the server's deployment path for your environment.

## Requirements

- Ansible Core 2.16 or newer
- Linux managed hosts
- A Java runtime and an existing service definition when managing services
- Network access from managed hosts to the artifact URL
- `unzip` on managed hosts when artifacts use ZIP format
- For WAR deployments, an application-server deployment path that supports
  the configured symlink

## Roles

| Role | Purpose |
| --- | --- |
| `preflight` | Validate inputs, paths, operation mode, and enabled options. |
| `download` | Download a ZIP or TAR.GZ archive from a supplied URL, with optional credentials and checksum. |
| `deploy` | Safely extract the archive, stage an immutable versioned release, and activate its `current` symlink. |
| `healthcheck` | Retry an HTTP(S) endpoint until the configured status is returned. |
| `release` | Orchestrate download, deployment, service management, health verification, and recovery. |
| `rollback` | Activate a retained release or the previously recorded release. |

## Quick start

```yaml
---
- name: Deploy a Java application
  hosts: java_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.release
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: >-
          https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.tar.gz
        java_archive_artifact_path: app/orders-api.jar
        java_artifact_sha256: "{{ artifact_sha256 }}"
        java_base_dir: /opt/apps/orders-api
        java_manage_service: true
        java_service_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
        java_artifact_username: "{{ vault_nexus_username }}"
        java_artifact_password: "{{ vault_nexus_password }}"
```

Store credentials in Ansible Vault or an Automation Controller credential.
Do not put credentials in URLs, playbooks, or inventory. The download task
suppresses output when authentication is configured.

Set `java_artifact_url` to the complete HTTP(S) URL of the archive. The URL
must end in `.zip` or `.tar.gz`; an optional query string is supported. The
collection infers the archive format from the URL and extracts it after
download. Set `java_archive_artifact_path` to the relative path of the JAR or
WAR within the archive (default: `<java_app_name>.<type>`). Keep repository
credentials in the supported authentication variables rather than embedding
them in the URL.

For a WAR, set `java_artifact_type: war` and `java_war_deploy_path` to the
application server's expected WAR file path (for example, a dedicated
`webapps/orders.war` path). The collection points that path at the selected
WAR under the active release; configure and test symlink support in the
application server and filesystem.

## Release layout and operations

By default, releases are stored in
`<java_base_dir>/releases/<java_app_version>/`, with extracted archive content
and a stable `<java_app_name>.<type>` link to the configured deployable.
`<java_base_dir>/current` points to the active version directory. Downloaded
archives are cached below `<java_base_dir>/cache`; the cache is not
automatically pruned. Release directories are immutable: use a new version
for changed content.

The `release` role runs preflight, download, staging and activation, optional
service restart/reload, then health verification. When a failure occurs after
activation, it attempts to restore the prior active version if automatic
rollback is enabled and a prior retained version exists. Failed deployments
remain failed Ansible jobs even if recovery succeeds. A `java_result` fact
records the outcome.

The `rollback` role uses `java_rollback_target_version` when supplied;
otherwise it reads the previous version recorded by a successful deployment
or rollback from `<java_base_dir>/.java_ops_previous`.

## Operational considerations

- Provide `java_artifact_sha256` from trusted build metadata to verify
  integrity. A digest downloaded from the same untrusted source does not
  establish artifact provenance.
- Use HTTPS and keep certificate validation enabled. Private CA configuration
  belongs in the managed host's trust store.
- Serialize jobs modifying the same application across all controllers; this
  collection does not provide a distributed lock.
- Use `serial: 1` to sequence hosts in a play. It is not canary traffic
  management or traffic draining.
- Health checks are application-specific. This collection does not reverse
  database migrations or external side effects.
- `java_keep_releases` controls pruning only when explicitly enabled. Do not
  enable pruning until the retention policy and recovery window are understood.
- Check mode cannot prove successful download, service behavior, or endpoint
  health.

See [configuration.md](docs/configuration.md) and
[deployment-guide.md](docs/deployment-guide.md) for variables, JAR/WAR
examples, rollback, and operational guidance.

## Build and validate

The collection must be installed before a playbook can resolve fully qualified
role names such as `mayankjain_sudo.java_ops.release`. A source checkout at
`collections/mayankjain_sudo/java_ops` is not itself an Ansible collection
search-path entry. Build and install it from this collection root:

```sh
ansible-galaxy collection build
ansible-galaxy collection install mayankjain_sudo-java_ops-1.0.0.tar.gz
```

Then run the local example with an explicit localhost inventory:

```sh
ansible-playbook -i localhost, playbooks/deploy.yml
```

The comma makes `localhost,` an inline inventory and avoids Ansible's
implicit-localhost warning. For managed servers, configure an inventory that
contains the playbook's host group (for example, `java_servers`) and pass it
with `-i inventory.ini` instead. Install the rebuilt collection again after
changing its source files.

Run validation from this collection root:

```sh
ansible-lint
ansible-test sanity
```
