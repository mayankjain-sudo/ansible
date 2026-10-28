# `mayankjain_sudo.dnf_compat`

Install and remove packages on Enterprise Linux 8 hosts by invoking the `dnf`
command-line client through Ansible's `raw` module. This avoids importing
`python3-dnf` into the interpreter used by Ansible on the managed host.

The collection targets AlmaLinux 8, Rocky Linux 8, and RHEL 8. It requires
Ansible Core 2.17 or newer and a working SSH connection with permission to run
`dnf` (normally with `become: true`).

## Usage

```yaml
---
- name: Manage packages on EL8
  hosts: el8_hosts
  gather_facts: false
  become: true
  tasks:
    - name: Install required packages
      ansible.builtin.include_role:
        name: mayankjain_sudo.dnf_compat.packages
      vars:
        dnf_compat_packages:
          - git
          - rsync
        dnf_compat_state: present
```

Set `dnf_compat_state` to `absent` to remove the listed packages. It defaults
to `present`. Package entries must be RPM package names containing only
letters, digits, `.`, `_`, `+`, `:`, or `-`.

The role uses `rpm` to determine whether a requested change is needed, then
calls `dnf -y install` or `dnf -y remove` only when necessary. In check mode it
reports a pending change without invoking DNF.

## Limitations

- Fact gathering must be disabled when the selected remote Python interpreter
  cannot execute Ansible modules. The role itself uses `raw` for remote
  operations and does not require Python on the managed host.
- This role manages package presence only. It does not provide `latest`,
  package groups, repository configuration, cache management, or options for
  DNF transaction behavior.
- Package names are RPM names, not shell expressions, DNF groups, or package
  specifications with version constraints.
- The role is intended for EL8 systems with `rpm` and `dnf` installed.
