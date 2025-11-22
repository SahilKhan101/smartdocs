# Troubleshooting & Known Issues

This document contains a collection of known issues, error codes, and community-sourced workarounds for the OmegaCore runtime environment.

## Critical Error Codes

### ERR_QUANTUM_DECOHERENCE (Code 501)
**Severity:** Critical
**Affected Versions:** v4.0.0 - v4.2.1
**Description:**
This error occurs when the local state vector diverges from the global consensus on the OmegaCloud. It is often caused by high network jitter (>150ms) or when running on non-ECC RAM hardware.

**Stack Trace Example:**
```
CRITICAL:omegacore.quantum.state:Decoherence detected at block 0x4F3A
Traceback (most recent call last):
  File "/usr/local/lib/python3.9/site-packages/omegacore/quantum.py", line 402, in sync_state
    raise DecoherenceError("Vector mismatch: local=0.992, remote=0.441")
omegacore.exceptions.DecoherenceError: Vector mismatch: local=0.992, remote=0.441
```

**Workaround:**
1.  **Network Check:** Ensure your connection is stable.
2.  **Config Override:** You can force a "soft sync" by setting the environment variable `OMEGA_ALLOW_DRIFT=1`.
    *   *Warning:* This may cause data corruption if used during a write transaction.
3.  **Fallback:** If the issue persists, switch to hybrid mode in `omega.config.json`:
    ```json
    {
      "quantumMode": "hybrid",
      "driftTolerance": 0.05
    }
    ```

### ERR_NEURAL_OOM (Code 409)
**Severity:** Moderate
**Description:**
The Neural Compression engine (NCE) attempts to allocate more VRAM/RAM than is available. This is common when processing streams larger than 4GB on consumer hardware.

**Logs:**
`[NCE-Worker-0] WARN: Allocation failed for tensor shape [4096, 4096, 128]. Retrying with CPU offload...`
`[NCE-Worker-0] ERROR: OOM. System memory: 85% used.`

**Fix:**
*   **Linux:** Increase swap space.
*   **Config:** Set `compressionLevel` to `low`.
*   **Batching:** Process files in chunks smaller than 500MB.

## Legacy Issues (v3.x)

> [!WARNING]
> Support for v3.x ended on Jan 1st, 2024. Upgrade immediately.

*   **Issue #342:** `AlphaLib` conflict. If you have `alphalib` installed, OmegaCore v3 will crash on import.
    *   *Fix:* `pip uninstall alphalib` before installing `omegacore`.
*   **Issue #881:** Memory leak in `StreamReader`.
    *   *Fix:* Manually call `reader.close()` or use the context manager `with OmegaClient() as client:`.

## Community FAQ

**Q: Why does my CPU usage spike to 100% on startup?**
A: OmegaCore performs a "Entropy Check" on initialization. This generates 1GB of random noise to seed the CSPRNG. You can disable this for dev environments by passing `skip_entropy=True` to the constructor, but **NEVER** do this in production.

**Q: I'm getting `InvalidSignature` errors when verifying backups.**
A: Are you using the `secp256k1` curve? We migrated to `ed25519` in v4.1. If you have old backups, you need to use the `omega-migrate` tool to re-sign them.
```bash
omega-migrate --input ./backup.db --target-version 4.2 --key ./private.pem
```

**Q: Does it work with Docker?**
A: Yes, but you need to pass `--privileged` if you are using the hardware RNG features. Otherwise, it falls back to `/dev/urandom`.
