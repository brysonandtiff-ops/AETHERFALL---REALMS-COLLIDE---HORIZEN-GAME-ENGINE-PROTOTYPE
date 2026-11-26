# Android local downloads — AETHERFALL

**Canonical on-phone location seen in the owner's screenshot:**

```text
Internal storage/
└── AETHERFALL – REALMS COLIDE/
    ├── korvex_blockout_v01/   ← existing; untouched
    └── Docs/
        └── Inbox/             ← target for downloaded local documents
```

The local spelling **COLIDE** and the en dash are intentional: they match the **existing phone folder**. The GitHub project name remains *AETHERFALL — REALMS COLLIDE*; do **not** create a duplicate phone folder with a different spelling. This is a document-intake rule, not a renaming job.

## Two ways to put downloaded documents there

### Android My Files — simplest

1. Download your PDF, DOCX, Markdown or other document normally.
2. Open **My Files → Internal storage → Download**.
3. Select the downloaded document and choose **Move** (or **Copy** if you want to keep the original).
4. Open **Internal storage → AETHERFALL – REALMS COLIDE → Docs → Inbox**, creating `Docs` and `Inbox` if missing, then **Move here/Copy here**.

### Optional Termux command — repeatable and non-destructive

Run `termux-setup-storage` and grant Android access **once**. The command must run from a checkout of this repository on the phone. By default it only previews; it does not scan your entire phone, install a service or move files.

```sh
python3 tools/phone_docs.py --status
python3 tools/phone_docs.py --file AETHERFALL_Concept_Brief.pdf
python3 tools/phone_docs.py --file AETHERFALL_Concept_Brief.pdf --apply
```

The last command copies into `~/storage/shared/'AETHERFALL – REALMS COLIDE'/Docs/Inbox/`, verifies SHA-256 and **preserves the original Download file**. If a different document already has the same name, the tool creates a checksum-suffixed copy rather than overwriting.

For batches, rename **only the new downloaded documents** to start with `AETHERFALL_`, `Korvex_`, `Vellaris_` or another allowed character marker. Then:

```sh
python3 tools/phone_docs.py --scan
python3 tools/phone_docs.py --scan --apply
```

Optional **visible, foreground** intake while you use Termux:

```sh
python3 tools/phone_docs.py --scan --apply --watch --poll-seconds 20
```

This watches the top level of Download for project-named documents only. It waits for the file size/time to remain stable between scans. Stop with Ctrl+C. **No background service is installed or started automatically**, and Android may suspend Termux.

## What it does NOT do

- It **cannot change ChatGPT's or Android's default download destination**, silently move attachments from another app, or create a service from GitHub alone.
- It does not automatically access restricted app storage or copy anything until the owner gives device permission and runs it.
- It does not touch existing `korvex_blockout_v01`, pictures, reference art, Blender models, `.glb`, APKs, passwords, or unrelated downloads.
- It does not sync files to GitHub or connect S.I.R.E. AI. Local copies are not Git commits or real gameplay evidence.

Original artwork and models have a separate approved asset intake. Do not treat documentation as 3D/game runtime proof.

**Verification:** `python3 -m unittest discover -s tests -v` runs sandboxed file-copy tests; physical Android installation and storage permission remain **NOT VERIFIED**.
