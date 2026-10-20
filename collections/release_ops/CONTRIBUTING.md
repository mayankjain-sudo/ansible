# Contributing

1. Keep public role variables prefixed with `release_`.
2. Make changes idempotent and avoid shell parsing; use `command` with `argv`
   when a command is unavoidable.
3. Add or update tests for success, validation, and recovery behavior.
4. Run `ansible-lint` and `ansible-test sanity` from this collection directory.
5. Exercise deployment and rollback against a disposable Linux target before
   proposing changes.

Do not include credentials, production data, or untrusted archives in tests.
