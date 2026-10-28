# `mayankjain_sudo.dnf_compat.packages`

Manage RPM package presence on EL8 hosts through the DNF CLI, without using
the Python DNF bindings.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `dnf_compat_packages` | `[]` | Non-empty list of RPM package names to manage. |
| `dnf_compat_state` | `present` | Desired state: `present` or `absent`. |

Use the collection README for a complete playbook example and limitations.
