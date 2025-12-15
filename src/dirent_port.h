#pragma once

#if defined(_WIN32)

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <stdlib.h>
#include <string.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

struct dirent {
  char d_name[MAX_PATH + 1];
};

typedef struct DIR {
  HANDLE hFind;
  WIN32_FIND_DATAA ffd;
  struct dirent ent;
  int first;
  char pattern[MAX_PATH + 4];
} DIR;

static DIR *opendir(const char *name) {
  if (!name || !name[0]) return NULL;

  DIR *d = (DIR *)calloc(1, sizeof(DIR));
  if (!d) return NULL;

  // pattern = "<name>\*"
  snprintf(d->pattern, sizeof(d->pattern), "%s\\*", name);

  d->hFind = FindFirstFileA(d->pattern, &d->ffd);
  if (d->hFind == INVALID_HANDLE_VALUE) {
    free(d);
    return NULL;
  }
  d->first = 1;
  return d;
}

static struct dirent *readdir(DIR *d) {
  if (!d) return NULL;

  while (1) {
    if (d->first) {
      d->first = 0;
    } else {
      if (!FindNextFileA(d->hFind, &d->ffd)) return NULL;
    }

    // Skip "." and ".."
    if (strcmp(d->ffd.cFileName, ".") == 0 || strcmp(d->ffd.cFileName, "..") == 0) continue;

    strncpy(d->ent.d_name, d->ffd.cFileName, sizeof(d->ent.d_name) - 1);
    d->ent.d_name[sizeof(d->ent.d_name) - 1] = '\0';
    return &d->ent;
  }
}

static int closedir(DIR *d) {
  if (!d) return -1;
  if (d->hFind != INVALID_HANDLE_VALUE) FindClose(d->hFind);
  free(d);
  return 0;
}

#else
#include <dirent.h>
#endif
