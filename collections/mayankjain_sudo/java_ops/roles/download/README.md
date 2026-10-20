# `download` role

Downloads a ZIP or TAR.GZ archive from a user-supplied HTTP(S) URL to the
managed host's artifact cache. Requires Ansible Core 2.16 or newer.

## Usage

The `release` role calls this role as part of its workflow. Use it directly
when a pipeline needs to download an artifact separately:

```yaml
---
- name: Download a Java artifact
  hosts: java_servers
  become: true
  roles:
    - role: mayankjain_sudo.java_ops.download
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.tar.gz"
        java_archive_artifact_path: app/orders-api.jar
        java_artifact_sha256: "{{ artifact_sha256 }}"
        java_base_dir: /opt/apps/orders-api
        java_artifact_username: "{{ vault_nexus_username }}"
        java_artifact_password: "{{ vault_nexus_password }}"
```

Keep credentials in Ansible Vault or an Automation Controller credential.
Do not embed them in the URL. Output is suppressed when username/password or
bearer-token authentication is configured.

## URL and archive behavior

Set `java_artifact_url` to the complete HTTP(S) artifact URL, including the
repository host and path. It must end in `.zip` or `.tar.gz`; an optional query
string is supported. The URL suffix selects the archive format and cached
filename.

The role stores the archive at
`<java_artifact_cache_dir>/<java_app_name>-<java_app_version>.<archive-suffix>`
and exposes it as the `java_downloaded_artifact` fact. It does not extract or
activate the archive; the `deploy` role handles safe inspection and extraction.
Set `java_archive_artifact_path` to the relative path of the JAR/WAR inside the
archive; its default is `<java_app_name>.<java_artifact_type>`.

When `java_artifact_sha256` is set, Ansible verifies the downloaded file
against that checksum. Supply the digest from trusted build metadata
independent of the artifact source. TLS certificate validation is enabled by
default.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required | Application name used in the cached filename. |
| `java_app_version` | required | Version used in the cached filename. |
| `java_artifact_type` | `jar` | Deployable type, `jar` or `war`. |
| `java_artifact_url` | required | Complete HTTP(S) URL ending in `.zip` or `.tar.gz` (optional query string allowed). |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative deployable path inside the downloaded archive. |
| `java_artifact_cache_dir` | `{{ java_base_dir }}/cache` | Cache directory. |
| `java_artifact_sha256` | empty | Optional expected SHA-256 digest. |
| `java_artifact_username` | empty | HTTP Basic username; pair with password. |
| `java_artifact_password` | empty | HTTP Basic password. |
| `java_artifact_bearer_token` | empty | Bearer token; do not combine with Basic auth. |
| `java_artifact_timeout` | `30` | Download timeout in seconds. |
| `java_validate_certs` | `true` | Validate the HTTPS certificate. |
| `java_run_as_user` / `java_run_as_group` | `root` / `root` | Owner and group of cache and artifact. |

See the collection [configuration reference](../../docs/configuration.md) for
URL, credential-handling, and integrity requirements.
