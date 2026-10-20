# `healthcheck` role

Verifies application readiness by retrying an HTTP(S) GET request until the
configured status code is returned. Requires Ansible Core 2.18 or newer.

## Usage

```yaml
---
- name: Verify application health
  hosts: application_servers
  become: true
  roles:
    - role: mayankjain_sudo.release_ops.healthcheck
      vars:
        release_app_name: your-app
        release_healthcheck_url: http://127.0.0.1:8080/health
        release_expected_status: 200
        release_healthcheck_retries: 10
        release_healthcheck_delay: 3
        release_healthcheck_timeout: 5
```

## Behavior

With `release_healthcheck_enabled: true` (the default), the role uses
`ansible.builtin.uri` with method `GET`, certificate validation enabled, and
the configured timeout, retry count, and delay. Response content is not
returned or logged. Success sets the host fact
`release_healthcheck_status: healthy`. Exhausting retries fails the role with
a message identifying the application and expected status, without exposing
response content.

Set `release_healthcheck_enabled: false` to skip the request; the role sets
`release_healthcheck_status: healthcheck_skipped`. This role does not start or
restart a service. When used by the [`release` role](../release/README.md),
health-check failure can trigger automatic recovery.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `release_app_name` | required for failure reporting | Application identifier. |
| `release_healthcheck_enabled` | `true` | Whether to make the HTTP request. |
| `release_healthcheck_url` | empty | HTTP(S) endpoint; required when enabled. |
| `release_expected_status` | `200` | Expected HTTP status, from 100 to 599. |
| `release_healthcheck_retries` | `10` | Positive number of attempts. |
| `release_healthcheck_delay` | `3` | Non-negative seconds between attempts. |
| `release_healthcheck_timeout` | `5` | Positive per-request timeout in seconds. |

The `release_` variables are shared with other collection roles. See the
collection [configuration guide](../../docs/configuration.md) for details.
