# Installation & Advanced Configuration

## System Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **OS** | Ubuntu 20.04 / Windows 10 | Debian 12 / Windows 11 |
| **CPU** | 2 Cores | 8 Cores (AVX2 support required for Neural Engine) |
| **RAM** | 4 GB | 16 GB |
| **Network** | 10 Mbps | 1 Gbps (for real-time sync) |

> [!NOTE]
> ARM64 support (Apple Silicon, Raspberry Pi) is currently in **Beta**. You may experience segfaults in the `libomega_core.so` shared object when using high-precision floating point modes.

## Installation Methods

### Method 1: PyPI (Standard)
```bash
pip install omegacore
```
*Note: This installs the pre-compiled wheels. If you are on Alpine Linux, this will fail because of `glibc` dependencies.*

### Method 2: Build from Source (Advanced)
If you need custom compiler flags (e.g., `-O3` or `-march=native`):

1.  Clone the repo:
    ```bash
    git clone https://github.com/omegacore/source.git
    ```
2.  Install build deps:
    ```bash
    sudo apt-get install build-essential cmake libssl-dev
    ```
3.  Build:
    ```bash
    cd source && python setup.py build_ext --inplace
    ```

## Configuration File (`omega.config.json`)

The configuration file is complex. Here is a full example with all options:

```json
{
  "version": 4,
  "auth": {
    "apiKey": "oc_live_...",
    "rotationInterval": 86400
  },
  "network": {
    "endpoints": [
      "wss://api.omegacore.dev",
      "wss://backup-api.omegacore.eu"
    ],
    "proxy": {
      "enabled": false,
      "url": "http://proxy.corp.local:8080"
    },
    "ipv6": true
  },
  "performance": {
    "threadPoolSize": 12,
    "gpuOffload": "auto", // Options: "auto", "cuda", "rocm", "disabled"
    "cacheSizeMB": 512
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/omega/agent.log",
    "jsonFormat": true
  }
}
```

### Environment Variables
You can override any config using env vars with the `OMEGA_` prefix and double underscores for nesting.
*   `OMEGA_AUTH__APIKEY` overrides `auth.apiKey`
*   `OMEGA_PERFORMANCE__GPUOFFLOAD=disabled`

## Docker Setup

We provide an official image: `omegacore/runtime:latest`.

```yaml
version: '3'
services:
  app:
    image: omegacore/runtime:4.2
    environment:
      - OMEGA_AUTH__APIKEY=${API_KEY}
    volumes:
      - ./data:/app/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```
*Note: The Docker image is 1.2GB because it includes the CUDA 11.8 runtime.*
