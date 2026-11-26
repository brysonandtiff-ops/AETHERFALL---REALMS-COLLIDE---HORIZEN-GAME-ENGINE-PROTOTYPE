# Godot add-ons / third-party feature quarantine

Godot's recognised `res://addons/` directory lives here inside `game/`. Do not install plugins implicitly, mirror vendor source without license or assume Unreal `.uplugin` files are compatible.

For a real add-on, record vendor/source URL, licence, version and hash, risk review, enabled settings, supported Godot version, offline build behavior, conflict/rollback path, provenance and explicit owner approval. Add native import/start tests to CI. Do not commit credentials or vendor binary blobs without storage/rights approval.

Currently **no add-on is installed by this scaffold**; only this policy exists.
