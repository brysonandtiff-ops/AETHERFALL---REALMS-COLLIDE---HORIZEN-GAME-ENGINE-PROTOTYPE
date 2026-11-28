# AETHERFALL — Private S.I.R.E. source dependency

AETHERFALL is public; the owner's S.I.R.E. master repository is private. Keep the master software in its own private repository. The public game contains only this dependency contract, the existing project command interface, and read-only bridge code. No private code, private registry output, tokens, local models, backups or device configuration belong in public source, builds or CI artifacts. Do not bundle developer tools into the Godot export.

## Operator commands

1. On an already authorised development host, use a separate clean checkout of the owner's existing private S.I.R.E. repository. Review the pinned commit in `.sire/source-lock.json`; do not switch or discard an existing dirty working tree. Do not add credentials to this project. The bridge never clones, fetches, installs, starts a service or sends a job.
2. Run `python3 tools/sire_bridge.py contract` to verify the public dependency contract. Run `python3 tools/sire_bridge.py doctor --sire-root /path/to/private/SIRE` to verify the exact source identity, Git origin, clean tree and entrypoint bytes. A missing or wrong checkout returns exit 2; contract or execution error returns exit 1.
3. In the **private local terminal only**, run `python3 tools/sire_bridge.py catalog --sire-root /path/to/private/SIRE`. It runs the real upstream filesystem registry at the pinned commit and reads the professional studio capability IDs from pinned source. It does not make agents, plugins, model inference, game tools or remote execution live. Do not publish the resulting private catalogue.
4. Use the existing `tools/aetherfall.py` work-order/handoff workflow. An authorised existing S.I.R.E. master operator must accept the exact game source and handoff, check independent permissions, and return genuine source-bound evidence for each tool. No second master, new paid dependency, unrestricted command execution or automatic promotion.

## Capability acceptance

The private checkout gives access to the shared master source and its evolving registry, not automatic runtime authority. The professional studio registry is the required capability checklist, not a list of passing tests. Verify separately: project planning/source identity, native Godot and Blender, Android export/storage, controller/touch, audio, screenshots/video, performance, authenticated runner, artifact storage, save recovery, security, accessibility, independent reviewer/signature and exact release bytes. The full private registry also covers engineering, integration and other software capabilities; non-game tools remain on the authorised development host, not in the player build. Existing HORIZON integration branches and game assets require separate review and are preserved.

## Updating or rollback

Advance the version lock and corresponding independently reviewed source pins in a reviewable change only after running the bridge and real upstream tools on the authorised host. Public CI checks the source contract and unit tests without private credentials, checkout or networking; it cannot certify the master runtime. Roll back this integration change on its review branch, without altering main, original game assets, private source or saves.
