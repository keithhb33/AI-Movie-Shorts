#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// Log hook type (generator.c currently expects this name)
typedef void (*GeneratorLogHook)(const char *line);

// Optional alias if other files use a different typedef name
typedef GeneratorLogHook generator_log_hook_fn;

// Install/uninstall log hook (pass NULL to disable)
void generator_set_log_hook(GeneratorLogHook hook);

// Core generation entrypoint
int run_generation(void);

// Back-compat: older UI code calls generator_run()
#ifndef generator_run
  #define generator_run() run_generation()
#endif

#ifdef __cplusplus
}
#endif
