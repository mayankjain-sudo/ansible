# Java deployment guide

## Standalone executable JAR

Create a systemd unit outside this collection that launches the JAR through
the stable `current` link, for example:

```ini
[Service]
User=orders
Group=orders
ExecStart=/usr/bin/java -jar /opt/apps/orders-api/current/orders-api.jar
Restart=on-failure
```

Then deploy it with:

```yaml
---
- name: Deploy orders API
  hosts: java_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.release
      vars:
        java_app_name: orders-api
        java_app_version: "{{ app_version }}"
        java_artifact_type: jar
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders-api/{{ app_version }}/orders-api-{{ app_version }}.tar.gz"
        java_archive_artifact_path: app/orders-api.jar
        java_artifact_sha256: "{{ nexus_orders_api_sha256 }}"
        java_base_dir: /opt/apps/orders-api
        java_run_as_user: orders
        java_run_as_group: orders
        java_manage_service: true
        java_service_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
        java_artifact_username: "{{ vault_nexus_username }}"
        java_artifact_password: "{{ vault_nexus_password }}"
```

The service definition is an administrator-owned runtime contract. Set
`java_artifact_url` to the complete HTTP(S) URL for your Nexus artifact,
including the repository host and full archive path. It must end in `.zip` or
`.tar.gz`; this collection does not append a repository prefix. Keep
authentication in the dedicated credential variables, not in the URL.
Confirm that the service user can traverse the release paths and read the JAR.

## WAR in an application server

Configure the application server to monitor a dedicated WAR path that permits
a symlink. Point `java_war_deploy_path` at that exact WAR path; use
`java_service_name` for the app-server service if it should be restarted.
The collection creates the versioned WAR file and updates the active symlink
on deployment and rollback.

```yaml
---
- name: Deploy orders web application
  hosts: app_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.release
      vars:
        java_app_name: orders
        java_app_version: "{{ app_version }}"
        java_artifact_type: war
        java_artifact_url: "https://nexus.example.com/repository/releases/com/acme/orders/{{ app_version }}/orders-{{ app_version }}.zip"
        java_archive_artifact_path: target/orders.war
        java_artifact_sha256: "{{ nexus_orders_war_sha256 }}"
        java_base_dir: /opt/apps/orders
        java_war_deploy_path: /srv/tomcat/webapps/orders.war
        java_manage_service: true
        java_service_name: tomcat
        java_healthcheck_url: http://127.0.0.1:8080/orders/health
        java_artifact_bearer_token: "{{ vault_nexus_token }}"
```

Application servers differ in how they scan, copy, and unpack WAR files.
Validate symlink behavior, undeployment of old exploded directories, and
restart/reload semantics against your exact server/version before production.
This collection does not configure Tomcat, JBoss/WildFly, WebLogic, or WebSphere.

## Rollback

Use an explicit retained version or omit the target to use the version recorded
after the last successful release operation:

```yaml
---
- name: Roll back orders API
  hosts: java_servers
  become: true
  serial: 1
  roles:
    - role: mayankjain_sudo.java_ops.rollback
      vars:
        java_app_name: orders-api
        java_base_dir: /opt/apps/orders-api
        java_rollback_target_version: "3.8.0"
        java_manage_service: true
        java_service_name: orders-api
        java_healthcheck_url: http://127.0.0.1:8080/actuator/health
```

Supply the same `java_artifact_type`, `java_war_deploy_path` (for WAR),
service, and health-check settings used by the deployment. Rollback changes
the active pointer and does not reverse database migrations or external
side-effects.

## Operations

- Run jobs that modify the same application serially across all controllers.
- Enable pruning only after validating the backup/rollback window. Retention
  preserves the active and immediately previous version.
- Keep Nexus credentials in Vault or controller credentials. Prefer HTTPS,
  enable TLS verification, and use an independently trusted artifact digest.
- Check-mode output is not a live test of artifact download, service state, or
  application health.
