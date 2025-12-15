#include "platform_open.h"

#include <stdio.h>
#include <stdlib.h>

#if defined(_WIN32)
  #ifndef WIN32_LEAN_AND_MEAN
  #define WIN32_LEAN_AND_MEAN
  #endif
  #include <windows.h>
  #include <shellapi.h>
#endif

static void open_folder_fallback_shell(const char *cmd) {
  if (!cmd) return;
  (void)system(cmd);
}

void platform_open_folder(const char *path) {
  if (!path || !path[0]) return;

#if defined(_WIN32)
  ShellExecuteA(NULL, "open", path, NULL, NULL, SW_SHOWNORMAL);

#elif defined(__APPLE__)
  char cmd[8192];
  snprintf(cmd, sizeof(cmd), "open \"%s\"", path);
  open_folder_fallback_shell(cmd);

#else
  // Linux/BSD: open in background
  char cmd[8192];
  snprintf(cmd, sizeof(cmd), "xdg-open \"%s\" >/dev/null 2>&1 &", path);
  open_folder_fallback_shell(cmd);
#endif
}
