# Aurora — The Archive of Red Light

Part myth, part machine: Aurora is a toolkit and research suite for creating, protecting, and operating cryptographically-aware membership artifacts. It blends image steganography, card generation, secure configuration, and membership workflows into one archive — a practical system wrapped in a little of the mythic language of sigils and seals.

This README explains the project at both the technical and philosophical levels, and provides a safe path for contributors to work with the code without exposing secrets.

**What Aurora Is**
- Aurora is a set of Python modules and utilities for generating member cards, embedding small authenticated payloads into visual seals, compositing those seals onto card images, and scanning/extracting the embedded data. It is designed for research and private deployments where physical artifacts (cards) carry verifiable metadata.

**High-Level Concepts**
- Seal: a small, visually distinct emblem (RedSeal) that holds a compact, steganographic payload.
- Embedding: compact, capacity-aware encoding of member identifiers and a minimal integrity layer into the pixels of the seal.
- Compositing: placing an embedded seal onto a physical card image in a specific location and overlaying with alpha blending.
- Scanning & validation: extracting the seal region, decoding the payload, and verifying minimal integrity constraints.

**Core Components**
- `api_config_manager.py` ([api_config_manager.py](api_config_manager.py)) — secure local storage and management of API backends and encrypted API blobs (uses Fernet + PBKDF2-derived key). Keep `config/` and `.key` out of any public repository.
- `mutable_steganography.py` ([mutable_steganography.py](mutable_steganography.py)) — the project's steganography implementation: embedding and extraction routines, sync/async wrappers, and higher-level helpers. This file contains the actual algorithmic work and is a key intellectual piece of the project.
- `seal_compositor.py` ([seal_compositor.py](seal_compositor.py)) — compositing tools for resizing the RedSeal image, embedding data into the seal, and pasting it onto card images.
- `card_generation.py` ([card_generation.py](card_generation.py)) — helpers to create base card images and layouts used by the system.
- `card_scanner.py` ([card_scanner.py](card_scanner.py)) — routines that detect the card format, crop the seal region, and extract or validate the embedded payload.
- `member_manager.py` & `member_manager_gui.py` ([member_manager.py](member_manager.py), [member_manager_gui.py](member_manager_gui.py)) — storage and UI workflows for member records and administration.
- `payment_module.py` ([payment_module.py](payment_module.py)) — front-end collection of payment metadata (stores last-four only, CVV should never be persisted). Review before production deployment to ensure PCI compliance.
- `steganography_module.py` ([steganography_module.py](steganography_module.py)) — supplementary utilities and alternate implementations for stego operations.
- `seal_compositor.py` (convenience functions) and `card_scanner.py` (test harness) — quick-run commands for local experimentation.

**Architecture & Data Flow**
1. Generate or provide a base card image (512×768 typical) using `card_generation.py`.
2. The `RedSeal` image is resized and the minimal payload (member id, tier, version, small integrity token) is composed into a compact JSON-like structure.
3. `mutable_steganography.py` encodes that compact payload into pixel data in a capacity-aware manner and writes a new embedded-seal image.
4. `seal_compositor.py` pastes the embedded seal onto the bottom-left of the card (10px padding by default) and writes the final PNG.
5. To validate, `card_scanner.py` crops the expected seal region, extracts the payload, and checks required fields and flags.

**Security & Privacy**
- Secrets: Do not commit `config/`, `.env`, or any private keys. This repository intentionally ignores them via `.gitignore`.
- Key storage: `api_config_manager.py` persists an encrypted blob and a derived key file under `config/`. Treat `config/.key` and `config/api_config.enc` as sensitive artifacts and rotate any keys if they were ever exposed.
- Payment data: `payment_module.py` collects card metadata for UX purposes. It must not store CVV. For production, use a PCI-compliant tokenization gateway; do not persist PANs or CVVs in your database.
- Audit & dependencies: We include a `requirements.txt`. Run `pip-audit` or equivalent tooling before releasing or deploying. Example: `pip-audit -r requirements.txt`.

**Operational Guidance**
- Test fixtures: replace any real-card images with synthetic fixtures before publishing.
- Secrets removal: if secrets were committed previously, use `git-filter-repo` or the BFG Repo-Cleaner to scrub the history, then rotate keys. This is a destructive operation and must be coordinated with collaborators.
- Packaging: the steganography internals are the most sensitive intellectual property. If you plan to publish, consider providing a thin public wrapper and keeping the implementation in a private package.

**Developer Quickstart**
1. Create a venv and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run quick compositing test (example):

```bash
python seal_compositor.py
```

3. Run the scanner demo (example):

```bash
python card_scanner.py
```

Note: both scripts expect the `data/` and `test_data/` folders to exist and to contain sanitized fixtures. Do not put real member data into test fixtures committed to the repo.

**Testing & CI**
- Add unit tests that exercise embedding capacity limits and extraction robustness (edge cases: truncated payloads, alpha blending, resized seals).
- Add CI steps: `pip-audit`, linting, and unit tests on PRs. Dependabot alerts should be triaged promptly; when a dependency is flagged, update and re-run tests.

**Contributing & Security Contact**
- See `CONTRIBUTING.md` for contribution flow and `SECURITY.md` for how to report security issues privately (contact: bjornwalczak@gmail.com).

**Philosophy & Notes**
Aurora is intentionally ambiguous in language: it uses the motif of seals and sigils to describe deterministic data carriers. Practically, it is a small, careful system for embedding compact verifiable metadata into images intended for physical distribution. The mythic language helps convey purpose but the implementation should be treated with engineering rigor: audit dependencies, secure secrets, and never store payment or unmasked PII in round-trip logs or test fixtures.

---

If you want, I can:
- expand any component's technical docs (for example: a protocol spec for the seal payload),
- extract an API reference from the modules, or
- prepare a public vs private split (thin public wrappers + private implementation) and rewrite files appropriately.
