# Third-party code in the release downloads

This repo's own files (guides, `tools/`, `source/`, `controls/`) are MIT licensed (see [LICENSE](LICENSE)).
The release downloads also contain the third-party code listed here. Each part keeps its own license.
The license texts are in [LICENSES/](LICENSES).

## `beamng-vkd3d-3.1-arm64-oryon.wcp` and `beamng-vkd3d-3.1-arm64-generic.wcp`

The two packages have the same contents. The **oryon** one is compiled with `-mcpu=oryon-1` (Snapdragon 8 Elite /
8 Elite Gen 5). The **generic** one is plain ARMv8-A.

| DLL | Project | Version | License | Source | Changes |
|---|---|---|---|---|---|
| d3d12.dll, d3d12core.dll | vkd3d-proton | v3.1 | LGPL-2.1 | https://github.com/HansKristian-Work/vkd3d-proton/tree/v3.1 | none, built for aarch64-w64-mingw32 |
| dxgi.dll, d3d11.dll, d3d10core.dll, d3d9.dll, d3d8.dll | DXVK | v3.1.1 | zlib | https://github.com/doitsujin/dxvk/tree/v3.1.1 | none, built for aarch64-w64-mingw32 |
| d3dcompiler_47.dll | vkd3d (vkd3d-utils + vkd3d-shader) | vkd3d-1.19 | LGPL-2.1 | https://gitlab.winehq.org/wine/vkd3d/-/tree/vkd3d-1.19 | none, linked as d3dcompiler_47 with [d3dcompiler_47.def](source/build/d3dcompiler_47.def) |
| msvcp140.dll, msvcp140_atomic_wait.dll, vcruntime140.dll, vcruntime140_1.dll | Wine (Proton 10.0 ARM64EC, as shipped by GameNative) | 10.0 | LGPL-2.1 | https://gitlab.winehq.org/wine/wine, https://github.com/ValveSoftware/wine | none, copied unchanged from GameNative's `proton-10.0-arm64ec` package |
| vulkan-1.dll | this project | 1 | MIT | [source/vkshim](source/vkshim) | — |

Build instructions: [source/BUILD.md](source/BUILD.md).

## `Turnip-a8xx-r56-unstrict.zip`

| File | Project | Version | License | Source | Changes |
|---|---|---|---|---|---|
| libvulkan_freedreno.so | Killdos26/turnip-a8xx (Mesa Turnip 27.0.0-devel with Adreno 8xx fault mitigations) by kyudongkim | r56 | GPL-3.0 as a whole (Mesa is mostly MIT; some commits come from Droid-Deck/drivers, GPL-3.0) | https://github.com/Killdos26/turnip-a8xx/tree/r56 | 17 bytes of the Android extension allow-list changed from 0 to 1. See below. |

**What was changed:** the official `Turnip-27.0.0-devel-a8xx-r56-adrenotools.zip` was built with Mesa's
"android-strict" option, which hides these device extensions:
`VK_KHR_calibrated_timestamps, VK_KHR_compute_shader_derivatives, VK_KHR_dynamic_rendering_local_read,
VK_KHR_index_type_uint8, VK_KHR_line_rasterization, VK_KHR_load_store_op_none, VK_KHR_maintenance5,
VK_KHR_maintenance6, VK_KHR_maintenance7, VK_KHR_map_memory2, VK_KHR_shader_expect_assume,
VK_KHR_shader_float_controls2, VK_KHR_shader_maximal_reconvergence, VK_KHR_shader_quad_control,
VK_KHR_shader_relaxed_extended_instruction, VK_KHR_shader_subgroup_rotate, VK_KHR_vertex_attribute_divisor`.
[`tools/patch_r56.py`](tools/patch_r56.py) sets exactly these 17 entries of the table
(`vk_android_allowed_device_extensions`) to allowed. Nothing else changes. The closest source-level equivalent
is building r56 with Mesa's `-Dandroid-strict=false` option, which unblocks these and every other hidden extension.

Corresponding source: the Killdos26/turnip-a8xx repository at tag `r56`, plus `tools/patch_r56.py`.
To reproduce the exact file:

    python3 tools/patch_r56.py Turnip-27.0.0-devel-a8xx-r56-adrenotools.zip Turnip-a8xx-r56-unstrict.zip

The script checks the input (sha256 `fdfccd60…a7e74f`) and the output (sha256 `82f98e55…05a5fc0`).

## `BeamNG_Driving.icp`

A GameNative control profile made for this project (MIT). Generator: [controls/make_beamng_icp.py](controls/make_beamng_icp.py).

## Not included

No files from BeamNG.drive, GameNative, Steam or Qualcomm are included.
