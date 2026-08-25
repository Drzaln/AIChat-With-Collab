# -*- coding: utf-8 -*-
"""Build-Llama-CUDA-Release.py

One-time builder: produces a portable, self-contained llama-server (CUDA)
tarball you upload to your own GitHub Release, so future Kaggle/Colab runs
can download a prebuilt binary instead of compiling from source every time.

Run this ONCE, on Kaggle (T4), whenever you want a new build (e.g. after
bumping LLAMA_CPP_TAG). It does NOT start a chat server and does NOT need
a model download -- it only builds + packages the binary.

## Why this exists
ggml-org/llama.cpp does not publish an official prebuilt Linux+CUDA binary
(only Linux CPU-only, and CUDA for Windows) -- confirmed by inspecting their
release assets directly. So "prebuilt binary as the default install path"
(the goal) has to mean *your own* prebuilt, not a random third-party one.
This script builds it once; the consumer notebooks then prefer downloading
that release asset, falling back to a source build only if it's missing,
incompatible, or fails a sanity check.

## What you do with the output
1. Run this cell on Kaggle (Settings -> Accelerator -> GPU T4 x2, or T4 x1
   is fine too -- this only needs ONE GPU to build for sm_75).
2. When it finishes, a tarball + .sha256 file sit in /kaggle/working/.
   Download both from the Kaggle notebook's Output panel.
3. On GitHub: your repo -> Releases -> Draft a new release -> pick/create a
   tag (e.g. "llama-cuda-b10605") -> attach both files as release assets ->
   Publish.
4. Copy the release asset's download URL (see the printed instructions at
   the end) into GITHUB_RELEASE_URL in Collab-Llama.py / Kaggle-Llama.py.

Re-run this script whenever you bump LLAMA_CPP_TAG and want an updated
prebuilt; each run's tarball is self-describing (VERSION.txt) so the
consumer notebooks can tell whether a given release asset is still a good
match before trusting it.
"""

import subprocess, time, os, sys, shutil, hashlib, tarfile, glob

# =====================================================================
# CONFIGURATION -- keep this in sync with Collab-Llama.py / Kaggle-Llama.py
# =====================================================================

LLAMA_CPP_TAG = "b10605"

# T4 = compute capability 7.5. If you also plan to run this build on other
# GPUs later, add more archs semicolon-separated, e.g. "75;86" -- but that
# increases build time and binary size, and this project's notebooks only
# ever run on T4s, so 75-only keeps this fast and small on purpose.
CUDA_ARCH = "75"

BUILD_DIR = "/kaggle/working/llama.cpp" if os.path.isdir("/kaggle/working") else "/tmp/llama.cpp"
OUTPUT_DIR = "/kaggle/working" if os.path.isdir("/kaggle/working") else "/tmp"

# ── Utility functions (same shapes as the other notebook scripts) ───

def sh(cmd, check=True, quiet=False, capture=False):
    kw = dict(shell=True, check=check)
    if capture:
        kw.update(capture_output=True, text=True)
    elif quiet:
        kw.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.run(cmd, **kw)


def section(n, total, title):
    bar = "\u2500" * 64
    print(f"\n{bar}\n [{n}/{total}] {title}\n{bar}")


def run_with_retry(fn, max_attempts=3, label="operation"):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == max_attempts:
                raise
            wait_s = attempt * 5
            print(f"  \u21bb {label} failed ({e}); retry {attempt}/{max_attempts} in {wait_s}s...")
            time.sleep(wait_s)


print("\u2554" + "\u2550" * 64 + "\u2557")
print("\u2551  Build-Llama-CUDA-Release \u00b7 one-time prebuilt packager" + " " * 7 + "\u2551")
print("\u255a" + "\u2550" * 64 + "\u255d")

TOTAL = 6
SERVER_BIN = f"{BUILD_DIR}/build/bin/llama-server"

# ── 1. GPU CHECK ──────────────────────────────────────────────────
section(1, TOTAL, "GPU Check")
r = sh("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", check=False, capture=True)
if r.returncode != 0:
    print("  \u26a0\ufe0f No GPU detected. A GPU is required to build the CUDA backend.")
    sys.exit(1)
gpu_name = r.stdout.strip().splitlines()[0] if r.stdout.strip() else "unknown"
print(f"  GPU: {gpu_name}")

r = sh("nvcc --version", check=False, capture=True)
if r.returncode != 0:
    print("  \u274c nvcc not found. CUDA toolkit is required to build the CUDA backend "
          "(this should already be present on Kaggle's GPU image).")
    sys.exit(1)
nvcc_version_line = [l for l in r.stdout.splitlines() if "release" in l.lower()]
nvcc_version = nvcc_version_line[0].strip() if nvcc_version_line else r.stdout.strip().splitlines()[-1]
print(f"  {nvcc_version}")

# ── 2. INSTALL BUILD TOOLS ────────────────────────────────────────
section(2, TOTAL, "Install Build Tools")
sh("apt-get update -qq && apt-get install -y -qq cmake build-essential git", check=False, quiet=True)
r = sh("cmake --version", check=False, capture=True)
print(f"  {r.stdout.splitlines()[0] if r.returncode == 0 else 'cmake install failed'}")

# ── 3. CLONE + BUILD ──────────────────────────────────────────────
section(3, TOTAL, f"Clone + Build llama.cpp @ {LLAMA_CPP_TAG} (sm_{CUDA_ARCH})")

def clone_step():
    sh(f"rm -rf {BUILD_DIR}", check=False, quiet=True)
    sh(f"git clone --depth 1 --branch {LLAMA_CPP_TAG} "
       f"https://github.com/ggml-org/llama.cpp.git {BUILD_DIR}")

print(f"  \u231b Cloning...")
run_with_retry(clone_step, label="git clone")

r = sh(f"git -C {BUILD_DIR} rev-parse --short HEAD", check=False, capture=True)
commit_hash = r.stdout.strip() if r.returncode == 0 else "unknown"
print(f"  Commit: {commit_hash}")

print("  \u231b Configuring (CUDA, Release)...")
sh(
    f"cmake -B {BUILD_DIR}/build -S {BUILD_DIR} "
    f"-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES={CUDA_ARCH} "
    f"-DCMAKE_BUILD_TYPE=Release "
    f"-DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF"
)

print("  \u231b Compiling llama-server (this is the slow part -- grab a coffee)...")
t0 = time.time()
sh(f"cmake --build {BUILD_DIR}/build --config Release -j$(nproc) --target llama-server")
build_seconds = int(time.time() - t0)
print(f"  \u2705 Build finished in {build_seconds}s")

if not os.path.isfile(SERVER_BIN):
    print(f"  \u274c Build finished but {SERVER_BIN} was not produced. Check the build log above.")
    sys.exit(1)

# ── 4. SANITY CHECK ───────────────────────────────────────────────
section(4, TOTAL, "Sanity Check")
r = sh(f"{SERVER_BIN} --version", check=False, capture=True)
if r.returncode != 0:
    print(f"  \u274c llama-server --version exited with code {r.returncode} -- build is broken, not packaging it.")
    print(f"  stdout: {r.stdout}\n  stderr: {r.stderr}")
    sys.exit(1)
version_output = (r.stdout + r.stderr).strip()
print(f"  \u2705 llama-server runs: {version_output.splitlines()[0] if version_output else '(no output)'}")

# ── 5. PACKAGE (binary + its own .so deps, NOT system CUDA libs) ──
section(5, TOTAL, "Package Binary + Dependencies")

r = sh(f"ldd {SERVER_BIN}", check=False, capture=True)
if r.returncode != 0:
    print("  \u26a0\ufe0f ldd failed to run -- packaging binary alone (may be statically linked, or ldd unavailable)")
    project_libs = []
else:
    # Keep only .so files that live INSIDE the build tree (this project's own
    # libggml*/libllama/libmtmd), skip system libs (libc, libcuda, libcudart,
    # libcublas, etc.) -- those should come from whatever CUDA/driver is
    # already on the host machine at run time, not be frozen into this
    # tarball, since bundling a mismatched CUDA runtime is exactly the kind
    # of "silent incompatibility" this whole verify-before-trust design is
    # meant to avoid.
    project_libs = []
    for line in r.stdout.splitlines():
        if "=>" in line:
            path = line.split("=>")[-1].strip().split(" ")[0]
        else:
            path = line.strip().split(" ")[0]
        if path and os.path.isabs(path) and BUILD_DIR in path and os.path.isfile(path):
            project_libs.append(path)
    print(f"  Found {len(project_libs)} project-owned shared libraries to bundle:")
    for p in project_libs:
        print(f"    - {os.path.basename(p)}")

pkg_name = f"llama-cuda-sm{CUDA_ARCH}-{LLAMA_CPP_TAG}"
pkg_dir = f"/tmp/{pkg_name}"
sh(f"rm -rf {pkg_dir}", check=False, quiet=True)
os.makedirs(f"{pkg_dir}/lib", exist_ok=True)

shutil.copy2(SERVER_BIN, f"{pkg_dir}/llama-server")
for p in project_libs:
    shutil.copy2(p, f"{pkg_dir}/lib/")

# Portable launcher -- points LD_LIBRARY_PATH at the bundled lib/ dir next
# to wherever the tarball ends up extracted, so no patchelf/RPATH surgery
# is needed and it works regardless of extraction path.
launcher = (
    "#!/bin/bash\n"
    'DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
    'export LD_LIBRARY_PATH="$DIR/lib:$LD_LIBRARY_PATH"\n'
    'exec "$DIR/llama-server" "$@"\n'
)
with open(f"{pkg_dir}/run.sh", "w") as f:
    f.write(launcher)
os.chmod(f"{pkg_dir}/run.sh", 0o755)
os.chmod(f"{pkg_dir}/llama-server", 0o755)

# Self-describing metadata -- the consumer notebook's verification step
# reads this before trusting the release asset (spec: "verify binary
# version + CUDA backend" before use, don't blindly trust a downloaded bin).
built_at = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
version_txt = (
    f"llama_cpp_tag={LLAMA_CPP_TAG}\n"
    f"commit={commit_hash}\n"
    f"cuda_arch=sm_{CUDA_ARCH}\n"
    f"built_on_gpu={gpu_name}\n"
    f"nvcc={nvcc_version}\n"
    f"built_at={built_at}\n"
    f"build_seconds={build_seconds}\n"
    f"llama_server_version_output={version_output.splitlines()[0] if version_output else ''}\n"
)
with open(f"{pkg_dir}/VERSION.txt", "w") as f:
    f.write(version_txt)

tarball_path = f"{OUTPUT_DIR}/{pkg_name}.tar.gz"
with tarfile.open(tarball_path, "w:gz") as tar:
    tar.add(pkg_dir, arcname=pkg_name)

sha256 = hashlib.sha256()
with open(tarball_path, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        sha256.update(chunk)
digest = sha256.hexdigest()
sha_path = f"{tarball_path}.sha256"
with open(sha_path, "w") as f:
    f.write(f"{digest}  {os.path.basename(tarball_path)}\n")

tar_size_mb = os.path.getsize(tarball_path) / (1024 * 1024)
print(f"\n  \u2705 Packaged: {tarball_path} ({tar_size_mb:.1f} MB)")
print(f"  \u2705 Checksum: {sha_path}")

# ── 6. UPLOAD INSTRUCTIONS ─────────────────────────────────────────
section(6, TOTAL, "Next Steps: Upload to GitHub Releases")
print(f"""
  1. Buka tab 'Output' notebook Kaggle ini, unduh 2 file berikut:
       - {os.path.basename(tarball_path)}
       - {os.path.basename(sha_path)}

  2. Di GitHub repo kamu:
       Releases -> Draft a new release
       -> Tag: llama-cuda-{LLAMA_CPP_TAG}  (atau tag lain sesukamu)
       -> Attach both files sebagai release assets
       -> Publish release

  3. Salin URL release asset (klik kanan file -> Copy link) -- bentuknya:
       https://github.com/<user>/<repo>/releases/download/llama-cuda-{LLAMA_CPP_TAG}/{os.path.basename(tarball_path)}

  4. Tempel URL itu ke GITHUB_RELEASE_URL di Collab-Llama.py / Kaggle-Llama.py.
     Notebook konsumen akan:
       - download tarball itu
       - cocokkan VERSION.txt di dalamnya (tag, arch, versi nvcc) dengan
         environment yang sedang jalan
       - kalau cocok & lolos sanity check ('llama-server --version') -> pakai
       - kalau tidak cocok/gagal -> otomatis fallback build dari source

  VERSION.txt yang ikut terbundel:
{version_txt}
  Selesai -- script ini TIDAK menjalankan server / download model apa pun.
""")
