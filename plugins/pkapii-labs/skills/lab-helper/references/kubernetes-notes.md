# Kubernetes (kind) labs: pitfalls (Ubuntu 22.04 ARM64 guest)

Not a solution. Read the actual assignment first. These are things that broke or surprised during a real run.

## Install and cluster

- Assignments often pin an old kind version and amd64 binaries. On ARM use `.../bin/linux/arm64/kubectl` (`https://dl.k8s.io/release/$(curl -sSL https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl`) and `https://kind.sigs.k8s.io/dl/<version>/kind-linux-arm64`. Check `kind version`, `kubectl version --client`; kind needs Docker running.
- A cluster of 1 control-plane and 2 workers is three Docker containers. Give the VM 2 CPUs and 4 GB, or it crawls.
- Nodes stay `NotReady` for a few seconds after creation; wait, do not recreate.
- `kind create cluster --name <n> --config file.yaml`; `kind get clusters`; `kubectl config get-contexts`; `kind delete cluster --name <n>`.
- Between labs delete the previous cluster. Two kind clusters cannot publish the same host port.

## Reaching a NodePort from the Mac

- kind runs nodes in containers. A NodePort is reachable from outside only if the cluster config has `extraPortMappings` (containerPort = the NodePort, hostPort = a free port) on the control-plane node. It cannot be added later: recreate the cluster.
- The path is Mac port, VirtualBox NAT-network forward, VM port, kind port mapping, NodePort. Add the forward for that port in VirtualBox (see `vm-apple-silicon.md`).
- A NodePort number can belong to one Service only. If a previous exercise used it, delete those objects first.

## kubectl habits

- `kubectl get pods -o name` prints `pod/<name>`. Do not write `kubectl describe pod $(...)`; write `kubectl describe $(...)`.
- Take names from the live listing, not from `head -1`: after a restart the first line can be a Terminating pod. For logs use `kubectl logs deploy/<name>`.
- `kubectl run --rm -i ... | head` leaves the pod behind (`Completed`). Avoid piping those commands; delete leftovers.
- `kubectl rollout undo` prints a warning about `last-applied-configuration`; apply the manifest file again afterwards so it matches the cluster.
- After `rollout undo` the revision numbers do not go back: the old revision becomes a new one. `rollout history` shows `<none>` for change-cause unless you annotate.
- `kubernetes.io/change-cause` is copied to the current ReplicaSet. Set it **after** `kubectl set image`; set earlier, it also lands on the previous revision.
- Newer versions warn that `Endpoints` is deprecated in favor of EndpointSlices; the warning is noise in your output, not an error.
- `kubectl diff -f file.yaml` returns nothing when the cluster matches the file; useful as the final check.
- `ImagePullBackOff` after a deliberately wrong tag is the expected outcome of a failed-update experiment; the old ReplicaSet keeps serving while a new one cannot become ready.

## Behavior to observe and explain (in your own words)

- Deleting a pod managed by a Deployment: the ReplicaSet creates a replacement with a new name.
- Readiness probe failing: the pod stays Running but is removed from Service endpoints. Liveness failing: the container is restarted.
- Services select pods by labels; no matching labels means empty endpoints. `kubectl get endpoints <svc>` shows it.
- A Service routes to `targetPort` on the pod, which must match the container port.
- DNS names: `<svc>`, `<svc>.<ns>`, `<svc>.<ns>.svc.cluster.local`. Test from a pod with `getent hosts` or `nslookup`.
- `emptyDir` loses data with the pod; a PVC does not. For PostgreSQL on a volume mount with `subPath` so the `lost+found` directory does not break initialization.
- Secrets are base64, not encryption; use `stringData` in manifests for readability.

## Diagnosing a broken deployment (general method)

1. `kubectl get all,cm,secret,pvc -n <ns>`, then `describe` the object that is not Ready, then `kubectl get events --sort-by=.lastTimestamp`.
2. Pod status tells the class of problem: `CreateContainerConfigError` (missing ConfigMap/Secret key), `ImagePullBackOff` (image/tag/registry), `CrashLoopBackOff` (read `logs --previous`), Running but `0/1` (readiness), Running and Ready but unreachable (Service selector, targetPort, port mapping).
3. Check `kubectl get endpoints`, then test DNS and connectivity from inside a pod, then fix the smallest thing and re-check. Write down the evidence for each hypothesis you rejected too.
4. Finish with the whole path from outside, and `kubectl diff` against your corrected file.
