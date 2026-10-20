# Troubleshooting

| Symptom | Likely cause and action |
| --- | --- |
| Preflight rejects the host | Gather facts and target a Linux host. Confirm required paths are absolute and the version contains only allowed characters. |
| Artifact is missing or unreadable | Stage it on the managed host before running the role; verify permissions for the Ansible become user. |
| Archive format cannot be inferred | Use `.tar.gz` or `.zip`, or set `release_artifact_format` to the matching supported format. |
| ZIP extraction fails | Ensure `unzip` is installed on the managed host. |
| Checksum mismatch | Compare the artifact against its trusted pipeline-provided SHA-256; do not disable verification to bypass an unexplained mismatch. |
| Existing inactive release is refused | Release directories are immutable. Investigate the contents and deploy changed content under a new version. |
| Health check fails | Inspect service logs and endpoint reachability from the target host. The response body is intentionally not emitted. |
| `deployment_failed_rollback_succeeded` | The new release failed but recovery health verification passed. Correct the new release and rerun with a new version. |
| `deployment_failed_rollback_failed` | Inspect the active symlink, service, and prior release manually. The job fails and reports both the original deployment error and recovery error. |
| Automatic rollback unavailable | No prior active release existed, or automatic rollback was disabled. The failed version is retained; inspect host state before remediation. |
| Previous-version rollback has no target | No successful deployment has recorded a previous version. Supply `release_rollback_target_version`. |
| Concurrent deployment behavior | Serialize jobs across controllers; the collection intentionally does not claim a cross-controller lock. |

The health-check task suppresses request output to avoid leaking endpoint
details or response data. Its failure message includes the application,
attempt count, and expected status without exposing response content.
