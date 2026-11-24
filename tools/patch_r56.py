#!/usr/bin/env python3
"""Make "Turnip a8xx r56 unstrict" from the official Killdos26/turnip-a8xx r56 AdrenoTools zip.

Why: the official Android build hides 17 Vulkan KHR extensions (Mesa's "android-strict" allow-list).
One of them, VK_KHR_load_store_op_none, is required by DXVK, so BeamNG says "no rendering device".
This script flips those 17 entries of the allow-list from 0 to 1. Nothing else in the driver changes.

usage: python3 patch_r56.py Turnip-27.0.0-devel-a8xx-r56-adrenotools.zip Turnip-a8xx-r56-unstrict.zip
"""
import hashlib
import io
import json
import sys
import zipfile

LIB = 'libvulkan_freedreno.so'
ORIG_SHA256 = 'fdfccd6079960fbb15936fd5891c63b2481887fa8c7e37211a61786732a7e74f'
NEW_SHA256 = '82f98e554e6290528dec40fa6feeff4f7e2f430331adcf939be3e108c05a5fc0'
NAMES_OFF = 0x869b4c   # VkExtensionProperties[478] (260 bytes each): instance + device extension names
ALLOW_OFF = 0x8880c4   # bool[478]: Mesa's vk_android_allowed_{instance,device}_extensions
COUNT = 478
UNBLOCK = [
    'VK_KHR_calibrated_timestamps', 'VK_KHR_compute_shader_derivatives', 'VK_KHR_dynamic_rendering_local_read',
    'VK_KHR_index_type_uint8', 'VK_KHR_line_rasterization', 'VK_KHR_load_store_op_none', 'VK_KHR_maintenance5',
    'VK_KHR_maintenance6', 'VK_KHR_maintenance7', 'VK_KHR_map_memory2', 'VK_KHR_shader_expect_assume',
    'VK_KHR_shader_float_controls2', 'VK_KHR_shader_maximal_reconvergence', 'VK_KHR_shader_quad_control',
    'VK_KHR_shader_relaxed_extended_instruction', 'VK_KHR_shader_subgroup_rotate', 'VK_KHR_vertex_attribute_divisor',
]
META = {
    'schemaVersion': 1,
    'name': 'Turnip a8xx r56 unstrict',
    'description': 'Killdos26/turnip-a8xx r56 (Adreno 8xx GPU-fault crash protection on by default) with 17 hidden '
                   'KHR extensions unblocked (incl. VK_KHR_load_store_op_none for DXVK). GPL-3.0. '
                   'Source: github.com/Killdos26/turnip-a8xx tag r56 + tools/patch_r56.py',
    'author': 'kyudongkim (r56), unstrict patch: beamng-android-native',
    'packageVersion': '1',
    'vendor': 'Mesa',
    'driverVersion': 'Vulkan 1.4.363',
    'minApi': 28,
    'libraryName': LIB,
}


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    with zipfile.ZipFile(sys.argv[1]) as z:
        lib = bytearray(z.read(LIB))
    if hashlib.sha256(lib).hexdigest() != ORIG_SHA256:
        print('This is not the official r56 driver (sha256 mismatch). Download '
              'Turnip-27.0.0-devel-a8xx-r56-adrenotools.zip from github.com/Killdos26/turnip-a8xx/releases/tag/r56')
        return 1
    names = []
    for k in range(COUNT):
        raw = lib[NAMES_OFF + k * 260:NAMES_OFF + k * 260 + 256]
        names.append(raw[:raw.index(0)].decode())
    for name in UNBLOCK:
        k = names.index(name)
        assert lib[ALLOW_OFF + k] == 0, name
        lib[ALLOW_OFF + k] = 1
    assert hashlib.sha256(lib).hexdigest() == NEW_SHA256
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('meta.json', json.dumps(META, indent=2) + '\n')
        z.writestr(LIB, bytes(lib))
    open(sys.argv[2], 'wb').write(buf.getvalue())
    print(f'OK: unblocked {len(UNBLOCK)} extensions -> {sys.argv[2]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
