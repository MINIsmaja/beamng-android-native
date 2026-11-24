/* vulkan-1.dll shim for BeamNG's native Vulkan renderer under Wine (GameNative, ARM64).
 * Wine's winevulkan asserts (and aborts the game) when vkSetDebugUtilsObjectNameEXT fails on
 * the host driver. This shim hides VK_EXT_debug_utils / VK_EXT_debug_report from the instance
 * extension list and turns every debug-utils/report entry point into a no-op. Everything else
 * is forwarded to winevulkan.dll (see vulkan-1.def). */
#define VK_USE_PLATFORM_WIN32_KHR
#include <windows.h>
#include <string.h>
#include <vulkan/vulkan.h>

static HMODULE wv;
static PFN_vkGetInstanceProcAddr r_gipa;
static PFN_vkGetDeviceProcAddr r_gdpa;
static PFN_vkEnumerateInstanceExtensionProperties r_eiep;

static void init(void)
{
    if (wv) return;
    wv = LoadLibraryA("winevulkan.dll");
    r_gipa = (PFN_vkGetInstanceProcAddr)(void *)GetProcAddress(wv, "vkGetInstanceProcAddr");
    r_gdpa = (PFN_vkGetDeviceProcAddr)(void *)GetProcAddress(wv, "vkGetDeviceProcAddr");
    r_eiep = (PFN_vkEnumerateInstanceExtensionProperties)(void *)GetProcAddress(wv, "vkEnumerateInstanceExtensionProperties");
}

static int hidden(const char *n)
{
    return !strcmp(n, "VK_EXT_debug_utils") || !strcmp(n, "VK_EXT_debug_report");
}

/* ---- no-op debug entry points ---- */
static VkResult VKAPI_CALL s_SetObjectName(VkDevice d, const VkDebugUtilsObjectNameInfoEXT *i) { return VK_SUCCESS; }
static VkResult VKAPI_CALL s_SetObjectTag(VkDevice d, const VkDebugUtilsObjectTagInfoEXT *i) { return VK_SUCCESS; }
static void VKAPI_CALL s_QueueLabel(VkQueue q, const VkDebugUtilsLabelEXT *l) { }
static void VKAPI_CALL s_QueueEnd(VkQueue q) { }
static void VKAPI_CALL s_CmdLabel(VkCommandBuffer c, const VkDebugUtilsLabelEXT *l) { }
static void VKAPI_CALL s_CmdEnd(VkCommandBuffer c) { }
static VkResult VKAPI_CALL s_CreateMessenger(VkInstance i, const VkDebugUtilsMessengerCreateInfoEXT *ci,
        const VkAllocationCallbacks *a, VkDebugUtilsMessengerEXT *m) { *m = (VkDebugUtilsMessengerEXT)(uintptr_t)1; return VK_SUCCESS; }
static void VKAPI_CALL s_DestroyMessenger(VkInstance i, VkDebugUtilsMessengerEXT m, const VkAllocationCallbacks *a) { }
static void VKAPI_CALL s_SubmitMessage(VkInstance i, VkDebugUtilsMessageSeverityFlagBitsEXT s,
        VkDebugUtilsMessageTypeFlagsEXT t, const VkDebugUtilsMessengerCallbackDataEXT *d) { }
static VkResult VKAPI_CALL s_CreateReport(VkInstance i, const VkDebugReportCallbackCreateInfoEXT *ci,
        const VkAllocationCallbacks *a, VkDebugReportCallbackEXT *cb) { *cb = (VkDebugReportCallbackEXT)(uintptr_t)1; return VK_SUCCESS; }
static void VKAPI_CALL s_DestroyReport(VkInstance i, VkDebugReportCallbackEXT cb, const VkAllocationCallbacks *a) { }
static void VKAPI_CALL s_ReportMessage(VkInstance i, VkDebugReportFlagsEXT f, VkDebugReportObjectTypeEXT o,
        uint64_t obj, size_t loc, int32_t code, const char *layer, const char *msg) { }

static const struct { const char *name; PFN_vkVoidFunction fn; } stubs[] = {
    { "vkSetDebugUtilsObjectNameEXT",    (PFN_vkVoidFunction)s_SetObjectName },
    { "vkSetDebugUtilsObjectTagEXT",     (PFN_vkVoidFunction)s_SetObjectTag },
    { "vkQueueBeginDebugUtilsLabelEXT",  (PFN_vkVoidFunction)s_QueueLabel },
    { "vkQueueInsertDebugUtilsLabelEXT", (PFN_vkVoidFunction)s_QueueLabel },
    { "vkQueueEndDebugUtilsLabelEXT",    (PFN_vkVoidFunction)s_QueueEnd },
    { "vkCmdBeginDebugUtilsLabelEXT",    (PFN_vkVoidFunction)s_CmdLabel },
    { "vkCmdInsertDebugUtilsLabelEXT",   (PFN_vkVoidFunction)s_CmdLabel },
    { "vkCmdEndDebugUtilsLabelEXT",      (PFN_vkVoidFunction)s_CmdEnd },
    { "vkCreateDebugUtilsMessengerEXT",  (PFN_vkVoidFunction)s_CreateMessenger },
    { "vkDestroyDebugUtilsMessengerEXT", (PFN_vkVoidFunction)s_DestroyMessenger },
    { "vkSubmitDebugUtilsMessageEXT",    (PFN_vkVoidFunction)s_SubmitMessage },
    { "vkCreateDebugReportCallbackEXT",  (PFN_vkVoidFunction)s_CreateReport },
    { "vkDestroyDebugReportCallbackEXT", (PFN_vkVoidFunction)s_DestroyReport },
    { "vkDebugReportMessageEXT",         (PFN_vkVoidFunction)s_ReportMessage },
};

static PFN_vkVoidFunction stub(const char *n)
{
    for (unsigned i = 0; i < sizeof(stubs) / sizeof(stubs[0]); i++)
        if (!strcmp(n, stubs[i].name)) return stubs[i].fn;
    return NULL;
}

VKAPI_ATTR VkResult VKAPI_CALL vkEnumerateInstanceExtensionProperties(const char *layer, uint32_t *count, VkExtensionProperties *props)
{
    uint32_t n = 0, k = 0, i;
    VkExtensionProperties *all;
    VkResult r;

    init();
    if (layer) return r_eiep(layer, count, props);
    if ((r = r_eiep(NULL, &n, NULL)) < 0) return r;
    all = HeapAlloc(GetProcessHeap(), 0, (n ? n : 1) * sizeof(*all));
    if (!all) return VK_ERROR_OUT_OF_HOST_MEMORY;
    if ((r = r_eiep(NULL, &n, all)) < 0) { HeapFree(GetProcessHeap(), 0, all); return r; }
    for (i = 0; i < n; i++) if (!hidden(all[i].extensionName)) all[k++] = all[i];
    if (!props) { *count = k; r = VK_SUCCESS; }
    else {
        uint32_t c = *count < k ? *count : k;
        memcpy(props, all, c * sizeof(*all));
        *count = c;
        r = c < k ? VK_INCOMPLETE : VK_SUCCESS;
    }
    HeapFree(GetProcessHeap(), 0, all);
    return r;
}

VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(VkDevice d, const char *n)
{
    PFN_vkVoidFunction s;
    init();
    if (!n) return NULL;
    if (!strcmp(n, "vkGetDeviceProcAddr")) return (PFN_vkVoidFunction)vkGetDeviceProcAddr;
    if ((s = stub(n))) return s;
    return r_gdpa(d, n);
}

VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetInstanceProcAddr(VkInstance inst, const char *n)
{
    PFN_vkVoidFunction s;
    init();
    if (!n) return NULL;
    if (!strcmp(n, "vkGetInstanceProcAddr")) return (PFN_vkVoidFunction)vkGetInstanceProcAddr;
    if (!strcmp(n, "vkGetDeviceProcAddr")) return (PFN_vkVoidFunction)vkGetDeviceProcAddr;
    if (!strcmp(n, "vkEnumerateInstanceExtensionProperties")) return (PFN_vkVoidFunction)vkEnumerateInstanceExtensionProperties;
    if ((s = stub(n))) return s;
    return r_gipa(inst, n);
}
