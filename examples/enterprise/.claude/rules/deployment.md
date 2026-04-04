<important if="deploying, modifying CI/CD, or updating Kubernetes manifests">

## Deployment Procedures

- All deployments go through the CI/CD pipeline. Never deploy manually.
- Kubernetes manifests live in `deploy/`. Helm values in `deploy/values/`.
- Environment-specific config: `deploy/values/<env>.yaml` (dev, staging, prod).

### Pre-Deployment Checklist
1. All tests pass in CI (`bazel test //...`).
2. Docker images tagged with git SHA, not `latest`.
3. Database migrations applied before service deployment.
4. Feature flags verified in target environment.

### Rollback
- Rollback via `make rollback ENV=<env> SERVICE=<name>`.
- Never edit live Kubernetes resources directly (`kubectl edit` is forbidden).
- Post-rollback: create an incident ticket and investigate root cause.

### Secrets
- Managed via HashiCorp Vault. Never store in git, ConfigMaps, or env files.
- Access secrets through `pkg/config.Secret()` in Go code.
- New secrets: request via `#platform-secrets` Slack channel.

</important>
