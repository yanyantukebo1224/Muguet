# Muguet iOS Build

GitHub Actions build wrapper for the upstream [c22dev/muguet](https://github.com/c22dev/muguet) project.

This repository does not bundle GTA V game assets. It checks out a pinned upstream revision, precompiles the owner's own `game.wasm` for iOS, and produces an unsigned IPA artifact for sideloading.

## Current build target

- iOS device: arm64 (iPhone / iPad)
- Runner: GitHub-hosted macOS 26 arm64
- Xcode: 26+
- Rust: stable + 1.98.1 (the upstream iOS build toolchain)
- Install: AltStore is recommended by upstream

## Why the workflow needs only game.wasm

The iOS binary must contain the precompiled WebAssembly game code because iOS cannot JIT it at runtime. The much larger `data/` and `b/<build>/shaders/` asset folders are imported on the device after installation. Keep your original game-data ZIP private and import it in Muguet; it is not uploaded to this repository or to the build artifact.

The ZIP must contain `data/manifest.json`, `b/<build>/game.wasm`, and `b/<build>/shaders/`. The helper extracts only `game.wasm`.

## One-time setup

### 1. Prepare the WebAssembly file on your Windows PC

Install Python 3, download this repository, then run:

```powershell
py tools/extract-game-wasm.py "D:\path\to\your-game-data.zip" "C:\MuguetBuildInput\game.wasm"
```

The script prints the SHA-256 hash. Keep the original ZIP; you will import that ZIP into the iOS app later.

### 2. Share only game.wasm privately with Tailscale

Install and sign in to Tailscale on the Windows PC. Open **PowerShell as Administrator** and run:

```powershell
tailscale serve C:\MuguetBuildInput
```

Tailscale Serve makes the folder available only inside your tailnet (do not use Funnel). It prints an HTTPS URL similar to `https://your-pc.your-tailnet.ts.net`. The file URL is that address plus `/game.wasm`.

### 3. Add GitHub Actions secrets

In this repository, open **Settings → Secrets and variables → Actions → New repository secret** and add:

- `TS_OAUTH_CLIENT_ID`: Tailscale OAuth client ID
- `TS_OAUTH_SECRET`: Tailscale OAuth client secret
- `MUGUET_GAME_WASM_URL`: the private Tailscale Serve URL ending in `/game.wasm`
- `MUGUET_GAME_WASM_SHA256`: the SHA-256 hash printed by the extraction script

The Tailscale OAuth client must be allowed to create ephemeral CI devices with the `tag:ci` tag and the `auth_keys` write scope. Never paste OAuth credentials or other secrets into chat, commits, issues, or workflow logs.

### 4. Run the build

Open **Actions → Muguet iOS Build → Run workflow**. The default upstream revision is pinned to the commit shown in the workflow input. The build downloads only `game.wasm`, verifies its SHA-256, runs the upstream `make-ios.sh` pipeline, and uploads:

- `Muguet-iOS-IPA`: the unsigned IPA
- `Muguet-build-logs`: build log and manifest

The PC must remain online with Tailscale connected while the workflow downloads the file. After the download finishes, the PC can be disconnected.

## Install and import assets

1. Download `Muguet-iOS-IPA` from the successful Actions run.
2. Install the IPA with AltStore. The upstream README warns that other sideloading methods may not work correctly.
3. Open Muguet and import your original game-data ZIP. The app needs the data and shader folders; the game code is already embedded in the IPA.

A free Apple ID signing route is used for the IPA build. AltStore handles signing during installation; this is not an App Store-signed application.

## Troubleshooting

- **Tailscale download fails:** confirm the PC is online, Tailscale Serve is active, the OAuth client has the `tag:ci` permission, and the URL works from another device in the same tailnet.
- **Hash mismatch:** re-extract `game.wasm` and update the SHA-256 secret.
- **WASM build mismatch:** use the `game.wasm` from the same ZIP whose data/shaders you will import on the iPhone.
- **Build fails:** download `Muguet-build-logs` from the run and inspect `build.log` and `build-manifest.txt`.

## Upstream and license

The application source is maintained by [c22dev/muguet](https://github.com/c22dev/muguet) and is licensed under GPL-3.0. This repository is a CI/build wrapper, not a claim of authorship of the upstream application. The workflow records the exact upstream commit used for each build.
