# Building the release files yourself

Everything is cross-compiled on an x86-64 Linux PC with
[llvm-mingw](https://github.com/mstorsjo/llvm-mingw) **20261117 (ucrt, ubuntu-22.04-x86_64)**, targeting
`aarch64-w64-mingw32` (Windows on ARM64, which is what Wine ARM64EC runs).

In `build/build-arm64.txt` and `build/build-arm64-oryon.txt`, replace `@TOOLCHAIN@` with the path to llvm-mingw's
`bin` folder. The oryon file adds `-mcpu=oryon-1`.

## vkd3d-proton 3.1 and DXVK 3.1.1

```sh
git clone --recursive --branch v3.1   https://github.com/HansKristian-Work/vkd3d-proton vkd3d-proton-3.1
git clone --recursive --branch v3.1.1 https://github.com/doitsujin/dxvk dxvk-3.1.1
export PATH=/path/to/llvm-mingw/bin:$PATH
X=/path/to/source/build/build-arm64.txt        # or build-arm64-oryon.txt

cd vkd3d-proton-3.1
meson setup build --cross-file $X --buildtype release -Denable_tests=false -Db_lto=true -Db_lto_mode=thin
ninja -C build
cd ../dxvk-3.1.1
meson setup build --cross-file $X --buildtype release -Db_ndebug=if-release -Db_lto=true -Db_lto_mode=thin
ninja -C build
```

No source patches are needed for these versions. Then strip the DLLs with `aarch64-w64-mingw32-strip`:
- vkd3d-proton: `libs/d3d12/d3d12.dll`, `libs/d3d12core/d3d12core.dll`
- DXVK: `src/dxgi/dxgi.dll`, `src/d3d11/d3d11.dll`, `src/d3d10/d3d10core.dll`, `src/d3d9/d3d9.dll`, `src/d3d8/d3d8.dll`

## d3dcompiler_47 from vkd3d 1.19

Wine's own d3dcompiler_47 depends on wined3d and OpenGL, and GameNative ships an x64 OpenGL, so this one is built
from vkd3d's vkd3d-utils instead.

1. `git clone --branch vkd3d-1.19 https://gitlab.winehq.org/wine/vkd3d.git`, then `./autogen.sh`.
2. In a separate `build-arm64` folder:
   `../configure --host=aarch64-w64-mingw32 --enable-static --disable-shared --disable-tests --disable-demos --without-opengl`
   with `CPPFLAGS=-I<vulkan-headers>/include` and `LDFLAGS=-L<folder with a vulkan-1 import library>`.
   configure needs a Perl `JSON` module; `JSON::PP` from core Perl works through a tiny shim.
3. `make`. The command-line tools fail to link, which doesn't matter.
4. Compile vkd3d-utils' two `.c` files with `-DLIBVKD3D_UTILS_SOURCE -DLIBVKD3D_SHADER_SOURCE -DLIBVKD3D_SOURCE`.
5. Link them as a DLL with [d3dcompiler_47.def](build/d3dcompiler_47.def) against
   `.libs/libvkd3d.a`, `.libs/libvkd3d-shader.a` and `.libs/libvkd3d-common.a`.

## Wine runtime DLLs

`msvcp140.dll`, `msvcp140_atomic_wait.dll`, `vcruntime140.dll` and `vcruntime140_1.dll` are Wine's ARM64X builtins.
They're copied unchanged from the `system32` folder of GameNative's `proton-10.0-arm64ec` package.

## vulkan-1.dll (the shim)

```sh
aarch64-w64-mingw32-clang -O2 -shared -I<vulkan-headers>/include -o vulkan-1.dll vkshim/vkshim.c vkshim/vulkan-1.def -s
```

`vulkan-1.def` forwards every Vulkan export to `winevulkan.dll`, except the few the shim replaces.

## Packing the .wcp

A `.wcp` is an xz-compressed tar holding `profile.json` and the files it lists:

```sh
mkdir -p pkg/system32 && cp *.dll pkg/system32/
# pkg/profile.json: {"type":"VKD3D","versionName":"3.1-arm64-beamng","versionCode":1,"description":"...",
#   "files":[{"source":"system32/d3d12.dll","target":"${system32}/d3d12.dll"}, ...one entry per DLL...]}
cd pkg && tar -cJf ../beamng-vkd3d-3.1-arm64-generic.wcp profile.json system32
```

GameNative shows it as VKD3D version `<versionName>-<versionCode>`.

## The driver

See [THIRD_PARTY.md](../THIRD_PARTY.md#turnip-a8xx-r56-unstrictzip) and [tools/patch_r56.py](../tools/patch_r56.py).
