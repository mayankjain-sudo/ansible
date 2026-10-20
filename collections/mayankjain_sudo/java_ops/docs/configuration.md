# Configuration reference

All public variables use the `java_` prefix. The `release` role runs preflight,
download, deployment, and health verification in that order.

## Application and artifact

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required | Application identifier; letters, numbers, `_`, `.`, and `-`. |
| `java_app_version` | required for deploy | Version directory name; conservative alphanumeric, dot, underscore, plus, and hyphen form. `..` is rejected. |
| `java_artifact_type` | `jar` | Deployable type: `jar` or `war`. |
| `java_artifact_url` | required for deploy | Complete HTTP(S) URL of the archive. Must end in `.zip` or `.tar.gz`; an optional query string is supported. |
| `java_archive_artifact_path` | `{{ java_app_name }}.{{ java_artifact_type }}` | Relative path to the JAR/WAR file inside the downloaded archive. |
| `java_artifact_sha256` | empty | Optional 64-character expected SHA-256 digest. |
| `java_artifact_username` | empty | Optional repository username; pair with password. |
| `java_artifact_password` | empty | Optional repository password. Use Ansible Vault or a controller credential. |
| `java_artifact_bearer_token` | empty | Optional bearer token; mutually exclusive with username/password. |
| `java_artifact_timeout` | `30` | Download request timeout in seconds. |
| `java_validate_certs` | `true` | Validate TLS certificates. Install private CA certificates in the host trust store. |

The downloader uses `java_artifact_url` as supplied; the collection does not
select or hard-code a repository host. The URL must use HTTP or HTTPS, include
a host and artifact path, contain no parent-directory components, and end in
`.zip` or `.tar.gz` (before an optional query string); the archive format is
inferred from that suffix. Keep authentication in the dedicated variables,
not embedded in the URL.

The downloader suppresses task output when authentication is configured.
Credentials must not be embedded in the path. Use a checksum obtained from
trusted build metadata; a digest from the same untrusted source does not prove
provenance. Archive inspection rejects absolute/traversal names, links, and
unsupported entry types before extraction.

## Filesystem and ownership

| Variable | Default | Description |
| --- | --- | --- |
| `java_base_dir` | required | Absolute, non-root application root. |
| `java_releases_dir` | `{{ java_base_dir }}/releases` | Parent directory for immutable version directories. |
| `java_current_path` | `{{ java_base_dir }}/current` | Symlink to the active version directory. |
| `java_artifact_cache_dir` | `{{ java_base_dir }}/cache` | Download cache; it is not automatically pruned. |
| `java_war_deploy_path` | required for WAR | Exact WAR path watched by the application server. The collection manages this as a symlink. |
| `java_run_as_user` | `root` | Owner for release and cache files. |
| `java_run_as_group` | `root` | Group for release and cache files. |

Configured release, current, and cache paths must be normalized, distinct
descendants of `java_base_dir`; parent-directory (`..`) components are
rejected. The WAR deploy path must be absolute and must not contain `..`.
Configure the application server to support the managed symlink and ensure
its deployment path is dedicated to this application.
The extracted archive may place the deployable in a subdirectory; configure
`java_archive_artifact_path` to that archive-relative path. A stable link named
`<java_app_name>.<type>` is made in the release root for runtime integration.

## Service, health, recovery, and retention

| Variable | Default | Description |
| --- | --- | --- |
| `java_manage_service` | `false` | Apply service management after activation or recovery. |
| `java_service_name` | empty | Existing service to manage; required when enabled. |
| `java_service_state` | `restarted` | `started`, `restarted`, or `reloaded`. |
| `java_healthcheck_enabled` | `true` | Run an HTTP(S) health request. |
| `java_healthcheck_url` | empty | Endpoint required when health checks are enabled. |
| `java_expected_status` | `200` | Expected status code from 100 to 599. |
| `java_healthcheck_retries` | `10` | Positive number of requests. |
| `java_healthcheck_delay` | `3` | Non-negative delay in seconds. |
| `java_healthcheck_timeout` | `5` | Positive per-request timeout in seconds. |
| `java_auto_rollback` | `true` | Restore the previous version after post-activation failure. |
| `java_rollback_target_version` | empty | Explicit rollback version; empty uses the recorded previous version. |
| `java_keep_releases` | `5` | Number of release directories to retain when pruning is enabled. |
| `java_prune_releases` | `false` | Enable release cleanup after activation. Keep at least two versions. |

The collection does not install service definitions or configure an app server.
Create and test these runtime integrations separately. For WARs, the configured
service is generally the application-server service.

## Result fact

The `release` and `rollback` roles expose a host-level `java_result` fact.
Successful deployment, for example:

```yaml
java_result:
  app_name: orders-api
  requested_version: "3.8.1"
  previous_version: "3.8.0"
  active_version: "3.8.1"
  deployment_status: deployment_succeeded
  outcome: deployment_succeeded
  rollback_status: not_required
  healthcheck_status: healthy
```

Failures remain fatal to the play. Deployment errors and recovery status are
preserved in the result fact and task failure message.
