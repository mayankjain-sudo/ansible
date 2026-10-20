# `healthcheck` role

Checks Java application readiness by retrying an HTTP(S) GET request until the
configured status code is returned. Requires Ansible Core 2.16 or newer.

## Usage

The `release` and `rollback` roles invoke this role automatically. It can also
be used independently:

```yaml
---
- name: Verify Java application health
  hosts: java_servers
  gather_facts: true
  roles:
    - role: mayankjain_sudo.java_ops.healthcheck
      vars:
        java_app_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
        java_expected_status: 200
        java_healthcheck_retries: 10
        java_healthcheck_delay: 3
        java_healthcheck_timeout: 5
```

## Behavior

When enabled (the default), the role uses `ansible.builtin.uri` with method
`GET`, certificate validation enabled, and the configured timeout and retry
policy. It does not return or log response content. Success sets
`java_healthcheck_status: healthy`; failure is fatal and reports the app,
attempt count, and expected status.

Set `java_healthcheck_enabled: false` to skip the HTTP request. The role sets
`java_healthcheck_status: healthcheck_skipped`. It does not start or restart a
service.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_app_name` | required for failure reporting | Application identifier. |
| `java_healthcheck_enabled` | `true` | Whether to make the request. |
| `java_healthcheck_url` | empty | HTTP(S) endpoint; required when enabled. |
| `java_expected_status` | `200` | Expected status code from 100 to 599. |
| `java_healthcheck_retries` | `10` | Positive number of attempts. |
| `java_healthcheck_delay` | `3` | Non-negative seconds between attempts. |
| `java_healthcheck_timeout` | `5` | Positive request timeout in seconds. |

See the collection [configuration reference](../../docs/configuration.md) for
shared variable validation and usage.
