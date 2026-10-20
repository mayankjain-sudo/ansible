# Step-by-step deployment guide

This guide shows how to deploy an application archive with the
`mayankjain_sudo.release_ops` collection. It covers a source checkout, a
target-host artifact, a health-checked service, release verification, and
recovery. The same playbook can run locally, in CI, or as an Ansible Automation
Platform (AAP) Job Template.

The collection requires Ansible Core 2.18 or newer and a Linux managed host.
It uses versioned directories and an active symlink; it is not a container
deployment or a database migration system.

## Deployment flow at a glance

The `release` role:

1. Validates the release name, version, paths, Linux host, artifact, optional
   checksum, and configured service/health-check options.
2. Checks the current active release and creates an isolated staging directory
   under the releases directory.
3. Inspects archive paths and entry types. It rejects absolute or traversal
   paths, symbolic and hard links, unsupported entry types, malformed archive
   data, and empty archives.
4. Extracts the archive into staging and publishes it under its immutable
   version directory.
5. Switches the `current` symlink to the new release, applies the configured
   service action, and checks the health endpoint.
6. If a post-activation step fails, attempts to restore the previous active
   release when automatic rollback is enabled and a retained previous release
   is available.

A typical application directory looks like:

```text
/opt/apps/your-app/
├── current -> releases/1.0.1
├── releases/
│   ├── 1.0.0/
│   └── 1.0.1/
└── shared/
```

`shared/` is created for application data, but this collection does not mount
or link it into a release automatically. Configure the application to use it
or provide those links as a separate, deliberate step in your deployment
process.

## 1. Prepare the collection

From the collection root, build and install the collection into a collection
path available to your Ansible controller or execution environment:

```sh
cd collections/mayankjain_sudo/release_ops
ansible-galaxy collection build
ansible-galaxy collection install mayankjain_sudo-release_ops-1.0.0.tar.gz
```

For a repeatable production run, pin the collection version in the execution
environment or in a `requirements.yml`, and use a tested Ansible Core version
of 2.18 or newer.

Example `requirements.yml`:

```yaml
---
collections:
  - name: mayankjain_sudo.release_ops
    version: 1.0.0
```

Install it with:

```sh
ansible-galaxy collection install -r requirements.yml
```

The collection must also be present in the AAP execution environment when the
playbook is run as an AAP Job Template.

## 2. Prepare the application artifact

Build the application artifact in a controlled, trusted pipeline. Supported
formats are gzip-compressed tar archives (`.tar.gz`) and ZIP archives
(`.zip`). The archive should contain the files that belong at the root of the
release directory, for example:

```text
application.tar.gz
├── bin/
├── config/
└── VERSION
```

Before deploying:

- Put the archive on each managed host at an absolute path readable by the
  Ansible become user, such as
  `/var/tmp/releases/your-app-1.0.0.tar.gz`. The collection does not copy
  artifacts from the controller to managed hosts.
- Keep the artifact immutable after build. Do not replace an archive in place
  after computing its digest.
- Obtain the expected SHA-256 digest from trusted build metadata or another
  protected source independent of the artifact. Do not compute the expected
  value from the same untrusted file at deployment time.
- Use unique release versions for changed content. An inactive version
  directory is not overwritten.
- Do not package symlinks, hardlinks, device nodes, or other non-regular
  archive entries. The collection rejects them.

Transfer the artifact through your normal trusted delivery mechanism before
running the deployment play. For example, a pipeline may stage it with a
separate copy task; keep that task's source and credentials under the same
pipeline trust controls.

## 3. Prepare managed hosts and inventory

The target host must be Linux. The account used by Ansible needs permission to
read the archive and create or update the release directories and active
symlink. If the deployment manages a service, that account also needs
permission to perform the service action. Use `become: true` when appropriate.

The service should already be installed and configured to run the application
from the collection's `current` path. For example, an existing systemd unit
might use `/opt/apps/your-app/current/bin/start`. The collection does not
create a service unit or install system packages.

Create an inventory file, for example `inventory/production.yml`:

```yaml
---
all:
  children:
    application_servers:
      hosts:
        your-app-01.example.com:
        your-app-02.example.com:
```

Ensure the names in the inventory match the `application_servers` group used
by the playbook. Configure SSH connectivity, privilege escalation, and
credentials through your normal Ansible inventory, configuration, or AAP
Credential setup.

## 4. Create a deployment playbook

Create `deploy.yml` in your consumer project:

```yaml
---
- name: Deploy Your App
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.release
      vars:
        release_app_name: your-app
        release_version: "{{ app_version }}"
        release_base_dir: /opt/apps/your-app
        release_artifact_path: "{{ artifact_path }}"
        release_artifact_sha256: "{{ artifact_sha256 }}"

        release_run_as_user: your-app
        release_run_as_group: your-app

        release_manage_service: true
        release_service_name: your-app
        release_service_state: restarted

        release_healthcheck_enabled: true
        release_healthcheck_url: http://127.0.0.1:8080/health
        release_expected_status: 200
        release_healthcheck_retries: 10
        release_healthcheck_delay: 3
        release_healthcheck_timeout: 5

        release_auto_rollback: true
```

The application user and group must already exist on the managed hosts. If
your application runs as a different user, configure that identity instead.
The health-check URL is requested from the managed host, so use an address
reachable from that host, often a loopback address.

Required values for a typical deployment:

| Variable | Purpose |
| --- | --- |
| `release_app_name` | Stable identifier for the application. |
| `release_version` | New unique release directory name, such as `1.0.1`. |
| `release_base_dir` | Absolute root directory for releases, `current`, and `shared`. |
| `release_artifact_path` | Absolute path to the archive already staged on the managed host. |

When health checking is enabled (the default), also provide
`release_healthcheck_url`. When service management is enabled, provide
`release_service_name`. See the [configuration reference](configuration.md)
for all options.

## 5. Supply deployment inputs

Pass the version, artifact path, and trusted digest as variables. A local
variables file could look like this:

```yaml
---
app_version: "1.0.1"
artifact_path: /var/tmp/releases/your-app-1.0.1.tar.gz
artifact_sha256: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
```

In production, retrieve the digest from your trusted build/promotion system
and protect the variable source. Do not commit secrets or environment-specific
credentials to this file. If you intentionally do not configure checksum
verification, set `release_artifact_sha256` to an empty string; the archive
must still come from a trusted pipeline.

## 6. Check the playbook and run the deployment

From the consumer project directory, first syntax-check the playbook:

```sh
ansible-playbook \
  -i inventory/production.yml \
  --syntax-check \
  deploy.yml
```

Then run it with the approved variable source:

```sh
ansible-playbook \
  -i inventory/production.yml \
  -e @vars/your-app-production.yml \
  deploy.yml
```

Do not treat check mode as proof of a deployment. It cannot simulate archive
extraction, a real service action, active-link replacement, or a live health
check.

`serial: 1` updates one host at a time within this play execution. It does not
coordinate other controllers or other play runs. Serialize deployments to
the same application across all automation systems.

## 7. Verify the result

On success, the role sets a `release_result` fact for each host. A typical
result is:

```yaml
release_result:
  app_name: your-app
  requested_version: "1.0.1"
  previous_version: "1.0.0"
  active_version: "1.0.1"
  deployment_status: deployment_succeeded
  outcome: deployment_succeeded
  rollback_status: not_required
  healthcheck_status: healthy
  recovery_required: false
```

You can inspect the active link on a managed host with:

```sh
readlink -f /opt/apps/your-app/current
```

Also verify application behavior using your normal monitoring and smoke
checks. A successful HTTP status confirms only the configured health endpoint
responded as expected; it does not validate every application feature or
external dependency.

The archive is unpacked into `releases/<version>`. The `current` link is
updated only after staging completes. A deployment of the already-active
version does not re-extract that version. Use a new version for changed
content.

## 8. Understand failures and automatic recovery

Preflight and archive-staging failures occur before activation, so the active
symlink remains on the current release. If the service action or health check
fails after activation, `release_auto_rollback: true` (the default) attempts
to restore the previously active release when one exists. The deployment
still fails as an Ansible job, even if recovery succeeds; inspect the failure
output and `release_result` fields for the original error and recovery status.

Check the active link, service logs, endpoint reachability from the managed
host, and artifact provenance before retrying. See the
[troubleshooting guide](troubleshooting.md) for common failures.

## 9. Roll back explicitly when needed

The `rollback` role can restore a specific retained release:

```yaml
---
- name: Roll back Your app
  hosts: application_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.release_ops.rollback
      vars:
        release_app_name: your-app
        release_base_dir: /opt/apps/your-app
        release_rollback_target_version: "1.0.0"
        release_manage_service: true
        release_service_name: your-app
        release_service_state: restarted
        release_healthcheck_enabled: true
        release_healthcheck_url: http://127.0.0.1:8080/health
```

The target version must already exist under the configured releases directory.
The role validates that the current active release is retained so it can
attempt recovery if the requested rollback fails verification. A healthy
rollback reports `rollback_succeeded`. If the requested target fails but the
previous active version is restored and healthy, it reports
`rollback_failed`; an unsuccessful recovery reports `recovery_failed`. The
result preserves the original rollback error and any recovery error.

If `release_rollback_target_version` is omitted, the role uses the previous
version recorded after a successful deployment. See the
[configuration guide](configuration.md#example-explicit-rollback) for details.

## 10. Use the collection in AAP

For Ansible Automation Platform:

1. Include a tested version of this collection in the execution environment.
2. Store the playbook and inventory in the configured Project.
3. Configure an inventory group named `application_servers` or change the
   playbook's `hosts`.
4. Configure SSH and privilege escalation using an AAP Credential.
5. Stage the application archive on each managed host before the deployment
   Job Template runs.
6. Pass the release version and artifact path as validated non-secret inputs.
   Pass the expected digest from protected, trusted pipeline metadata.
7. Apply RBAC and approval controls to production deployment and rollback
   templates.
8. Capture Ansible job output and the `release_result` facts for audit.
9. Serialize jobs that can modify the same application, including jobs
   launched by other controllers.

See the [AAP integration guide](aap-integration.md) for additional
recommendations.

## Related documentation

- [Configuration reference](configuration.md)
- [Architecture and safety](architecture.md)
- [AAP integration](aap-integration.md)
- [Troubleshooting](troubleshooting.md)
- [Integration tests](../tests/README.md)
