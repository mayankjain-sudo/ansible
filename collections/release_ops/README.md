# Ansible Collection - `mayankjain_sudo.release_ops`

Roles for deploying trusted archive artifacts as immutable, versioned releases
on Linux hosts, switching an active symlink, checking health, and recovering to
the previously active release.

Requires Ansible Core 2.18 or newer.

This collection supports a single-host-at-a-time release-directory model. It
does not implement canary/rolling traffic management, database rollback,
container orchestration, or retention pruning.

## Roles

| Role | Purpose |
| --- | --- |
| `preflight` | Validate Linux, names, paths, archive, checksum, and enabled service/health options. |
| `deploy` | Stage the target-host archive in a unique temporary directory and activate a complete version directory. |
| `healthcheck` | Retry an HTTP(S) GET until the expected status is returned, or report an explicit skip. |
| `rollback` | Restore a named release or the version recorded by a successful deployment. |
| `release` | Run preflight, deployment, health verification, automatic recovery, and result reporting. |

## Quick start

```yaml
---
- name: Deploy an application release
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.release
      vars:
        release_app_name: payments-api
        release_version: "{{ app_version }}"
        release_base_dir: /opt/apps/payments-api
        release_artifact_path: "{{ artifact_path }}"
        release_manage_service: true
        release_service_name: payments-api
        release_healthcheck_url: http://127.0.0.1:8080/health
```

Review the full [configuration guide](docs/configuration.md), the
[architecture](docs/architecture.md), and the
[AAP integration guide](docs/aap-integration.md) before production use. For
an end-to-end walkthrough, see the
[step-by-step deployment guide](docs/deployment-guide.md).

## Artifact and filesystem contract

- `release_artifact_path` must point to an archive already present and readable
  on the managed Linux host. Controller-side copy/transfer is not performed.
- Supported archives are `.tar.gz` and `.zip`. ZIP extraction requires `unzip`.
- Optionally set `release_artifact_sha256` to a 64-character SHA-256 digest
  obtained from trusted build metadata, not from the artifact being checked.
- Archives must come from a trusted, controlled build pipeline. Before
  extraction, the collection rejects absolute and traversal paths, symbolic
  and hard links, unsupported entry types, and malformed archive data. Source
  trust and safe artifact handling remain required.
- The layout is `release_base_dir/releases/<version>`, a `current` symlink, and
  a separate `shared` directory. Configure `release_releases_dir`,
  `release_current_path`, and `release_shared_dir` only when needed.
- Existing inactive version directories are never overwritten. Use a new
  version for changed content. An already active version is not re-extracted.
- `release_run_as_user` and `release_run_as_group` default to `root`; set them
  explicitly if a different ownership model is required.

## Results and failure behavior

The orchestrator sets a host-level `release_result` fact with application,
requested/previous/active versions, deployment status, rollback status,
health-check status, and recovery details. A failed deployment remains a failed
Ansible job even if the prior release was restored successfully.

The result uses `deployment_succeeded` or `deployment_failed`; rollback status
is `not_required`, `rollback_succeeded`, `rollback_failed`, or
`rollback_unavailable`. Disabled health verification reports
`healthcheck_skipped`. The `outcome` field distinguishes
`deployment_failed_rollback_succeeded` from
`deployment_failed_rollback_failed`.

Automatic rollback is attempted only after the active pointer changed and a
prior release exists. Failed recovery is not hidden: the task failure includes
the original deployment error and recovery outcome.

## Limitations

- Jobs modifying the same application must be serialized externally. There is
  no cross-controller host lock.
- The collection does not prune old releases; `release_keep_releases` is
  reserved for future retention behavior and currently has no effect.
- `serial: 1` helps sequence hosts in one play but is not traffic draining or a
  canary strategy.
- A symlink update is performed with Ansible's file module. Atomic replacement
  depends on the target filesystem and Ansible implementation.
- Check mode cannot meaningfully simulate archive extraction, service
  behavior, or a live HTTP check. Do not treat check-mode output as proof of a
  successful release.

## Development

From the collection root, build and install the collection, then run:

```sh
ansible-galaxy collection build
ansible-galaxy collection install mayankjain_sudo-release_ops-1.0.0.tar.gz
ansible-lint
ansible-test sanity
ansible-playbook -i localhost, tests/integration/deploy.yml
```

The example playbooks in `playbooks/` use short role names resolved by the
collection-root `ansible.cfg`, so they can be syntax-checked directly from a
source checkout. Run them from the collection root. Consumer playbooks should
use the collection-qualified role names shown in the quick start after the
collection is installed in the execution environment.

The integration play requires a Linux host and privilege escalation for the
temporary release tree. See [testing notes](tests/README.md).
