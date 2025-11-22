# OmegaCore API Reference (v4.2.0)

## Global Configuration

The `OmegaClient` is the entry point. It is **not thread-safe** by default. For multi-threaded applications, use `OmegaPool`.

### `class OmegaClient(api_key: str, region: str = 'us-east-1', **kwargs)`

**Parameters:**
*   `api_key` (str): Required. The hex-encoded key from the console.
*   `region` (str): The data residency region.
*   `**kwargs`:
    *   `timeout` (int): Request timeout in seconds (default: 30).
    *   `retry_strategy` (RetryConfig): Custom retry logic.
    *   `debug_mode` (bool): If True, prints raw payloads to stdout.

**Example:**
```python
from omegacore import OmegaClient

# DANGEROUS: Don't hardcode keys!
client = OmegaClient("oc_live_7f8a9d...", debug_mode=True)
```

---

## Module: Cryptography (`omegacore.crypto`)

### `encrypt_data(payload, level='high', metadata=None)`

Encrypts a binary payload.

**Arguments:**
*   `payload` (bytes): Max size 2GB.
*   `level` (str):
    *   `'standard'`: AES-256-GCM (Fast)
    *   `'high'`: AES-256 + Kyber-1024 (Quantum Safe)
    *   `'paranoid'`: Cascaded encryption (AES -> Serpent -> Twofish). Very slow.
*   `metadata` (dict): Optional JSON-serializable metadata to attach to the header.

**Returns:**
`EncryptedObject` (dict-like):
*   `blob`: The encrypted bytes.
*   `iv`: Initialization vector.
*   `auth_tag`: GCM tag.
*   `algo_id`: The algorithm used (e.g., `alg_kyber_v3`).

**Raises:**
*   `PayloadTooLargeError`: If payload > 2GB.
*   `EntropyError`: If system entropy is low.

---

## Module: Neural Compression (`omegacore.neural`)

### `compress_stream(input_stream, output_stream, model='general_v4')`

**Note:** This function blocks until the stream is closed.

**Models:**
*   `'general_v4'`: Good for mixed data (JSON, CSV, Text). Ratio ~15:1.
*   `'image_gan_v2'`: Optimized for bitmaps. Lossy!
*   `'log_bert'`: Optimized for server logs. Ratio ~50:1.

**Example:**
```python
with open("large_log.txt", "rb") as f_in, open("compressed.oc", "wb") as f_out:
    # Use log_bert for massive log compression
    client.neural.compress_stream(f_in, f_out, model='log_bert')
```

---

## Deprecated Methods

### `client.legacy_connect()`
> [!CAUTION]
> **REMOVED in v4.0**. Do not use. This was used for the old WebSocket protocol. Use `OmegaSocket` instead.

### `client.set_master_key(key)`
> [!WARNING]
> Deprecated. Use `OmegaKeyManager` for key rotation. This method will raise a `DeprecationWarning` in v4.3 and `RuntimeError` in v5.0.
