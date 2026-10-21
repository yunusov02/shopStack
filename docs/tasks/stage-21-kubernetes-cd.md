# Stage 21: Kubernetes and CD

Prerequisites: stage 20.

- [ ] **S21.T01** k3d/kind cluster; Helm library chart + one chart per service (or umbrella)
  Must know: Kubernetes objects, Helm

- [ ] **S21.T02** Stateful deps: ADR 0043 operators vs managed; deploy Postgres, Kafka, RabbitMQ, Redis, MinIO
  Must know: StatefulSets, operators

- [ ] **S21.T03** Wildcard ingress, cert-manager DNS-01, host routing
  Must know: Ingress, TLS

- [ ] **S21.T04** Secrets (ADR 0044), rotation procedure for DB password and JWT keys; resource limits; probes; migration Jobs
  Must know: Secrets, Jobs, rotation

- [ ] **S21.T05** Network policies; internal API never exposed
  Must know: NetworkPolicy

- [ ] **S21.T06** Zero-downtime migrations with expand/contract; test under load
  Must know: expand/contract

- [ ] **S21.T07** Deployment strategies ADR 0045: rolling, blue-green, canary; rehearse rollback
  Must know: deployment strategies

- [ ] **S21.T08** Stateless services, no sticky sessions; HPA (CPU, RPS) and KEDA (queue length, lag); horizontal vs vertical scaling measured
  Must know: HPA, KEDA

- [ ] **S21.T09** High availability: SPOF list, Postgres failover, leader election for beat/relay (lease or Redis lock)
  Must know: HA, leader election

- [ ] **S21.T10** CD pipeline: per-service images, changed-only deploy, staging → approval → production
  Must know: GitHub Actions environments

- [ ] **S21.T11** Backup/restore drill on a fresh cluster (every DB + MinIO)
  Must know: `pg_dump`/PITR, MinIO mirror

- [ ] **S21.T12** Deploy to a real VPS/cloud
  Must know: cloud basics

- [ ] **S21.T13** `[EXT]` IaC with Terraform/OpenTofu; `[OPT]` ArgoCD GitOps
  Must know: Terraform, GitOps
