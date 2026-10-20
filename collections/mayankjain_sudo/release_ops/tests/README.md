# Integration testing

Run these tests on a disposable Linux host or execution environment with
Ansible Core installed. They use localhost, create temporary fixture
directories and local HTTP endpoints, and remove their fixtures when complete.
The tests do not require privilege escalation when the current user can write
to its temporary directory. For production-like testing, also run them in the
same image and with the same Ansible Core version used by your automation.

The collection requires Ansible Core 2.18 or newer. Build and install it from
the collection root before running the integration playbooks:

```sh
ansible-galaxy collection build
ansible-galaxy collection install mayankjain_sudo-release_ops-1.0.0.tar.gz
```

Run the successful deployment, idempotence, and immutable-content test:

```sh
ansible-playbook -i localhost, tests/integration/deploy.yml
```

It deploys a valid fixture archive, rebuilds that archive with different bytes
under the same version, reruns deployment, and verifies the existing release
content was not overwritten.

Run preflight, staging, automatic recovery, first-deployment, and explicit
rollback scenarios:

```sh
ansible-playbook -i localhost, tests/integration/deploy_failure_scenarios.yml
```

This covers:

- Invalid version input, a missing artifact, and a mismatched checksum.
- Malformed-archive failure during staging while the active release remains
  unchanged.
- Health failure after activation followed by successful automatic recovery.
- Health failure after activation followed by unsuccessful recovery, with
  both errors and the final active version checked.
- First deployment failing health verification when there is no prior release.
- Successful explicit rollback to a retained, healthy version.

Run archive path and entry-type checks:

```sh
ansible-playbook -i localhost, tests/integration/archive_safety.yml
```

It rejects traversal paths, tar symbolic and hard links, ZIP symbolic links,
and malformed tar/ZIP fixtures before activation. It verifies that the
pre-existing current symlink remains unchanged, then checks that a valid
archive still deploys.

Run explicit rollback recovery from an unhealthy target:

```sh
ansible-playbook -i localhost, tests/integration/rollback.yml
```

It attempts rollback from `1.0.1` to unhealthy `1.0.0`, then checks that
`1.0.1` was restored and verified, and that the failure result preserves the
original error.

Run rollback input and active-state validation tests:

```sh
ansible-playbook -i localhost, tests/integration/rollback_validation.yml
```

It verifies that missing health configuration, an invalid active symlink, a
missing rollback target, and overlapping configured paths fail before the
active pointer changes.

Check playbook parsing and lint separately:

```sh
ansible-playbook --syntax-check -i localhost, \
  tests/integration/deploy.yml \
  tests/integration/deploy_failure_scenarios.yml \
  tests/integration/archive_safety.yml \
  tests/integration/rollback.yml \
  tests/integration/rollback_validation.yml
ansible-lint
ansible-test sanity
```

Syntax checks and lint do not exercise runtime state transitions. The
integration playbooks intentionally expect some included role tasks to fail;
they rescue those failures and assert the resulting status, errors, and
filesystem state. A playbook passes only when those assertions pass.
