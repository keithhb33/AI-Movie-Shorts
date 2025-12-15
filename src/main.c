#include "raylib.h"
#include "generator.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#ifdef _WIN32
  #include <windows.h>
  #include <shellapi.h>
  static CRITICAL_SECTION g_log_lock;
  static void log_lock_init(void) { InitializeCriticalSection(&g_log_lock); }
  static void log_lock(void) { EnterCriticalSection(&g_log_lock); }
  static void log_unlock(void) { LeaveCriticalSection(&g_log_lock); }
#else
  #include <pthread.h>
  #include <unistd.h>   // getcwd
  static pthread_mutex_t g_log_lock = PTHREAD_MUTEX_INITIALIZER;
  static void log_lock_init(void) { /* nothing */ }
  static void log_lock(void) { pthread_mutex_lock(&g_log_lock); }
  static void log_unlock(void) { pthread_mutex_unlock(&g_log_lock); }
#endif

static volatile int g_running = 0;
static volatile int g_last_rc = 0;

#define LOG_MAX_LINES 300
#define LOG_LINE_MAX  600

static char g_log[LOG_MAX_LINES][LOG_LINE_MAX];
static int  g_log_head = 0;
static int  g_log_count = 0;

// UI font
static Font g_uiFont = {0};
static const float g_uiSpacing = 1.0f;

static void ui_log_hook(const char *line) {
  if (!line) return;
  log_lock();
  snprintf(g_log[g_log_head], LOG_LINE_MAX, "%s", line);
  g_log_head = (g_log_head + 1) % LOG_MAX_LINES;
  if (g_log_count < LOG_MAX_LINES) g_log_count++;
  log_unlock();
}

/* Portable "where am I running from?" */
static void get_working_dir(char *out, size_t outsz) {
  if (!out || outsz == 0) return;
#ifdef _WIN32
  DWORD n = GetCurrentDirectoryA((DWORD)outsz, out);
  if (n == 0 || n >= (DWORD)outsz) { out[0] = '.'; out[1] = 0; }
#else
  if (!getcwd(out, outsz)) { out[0] = '.'; out[1] = 0; }
#endif
}

static void open_folder_rel(const char *rel) {
  char cwd[1024];
  get_working_dir(cwd, sizeof(cwd));

  char full[2048];

#ifdef _WIN32
  snprintf(full, sizeof(full), "%s\\%s", cwd, rel);
  ShellExecuteA(NULL, "open", full, NULL, NULL, SW_SHOWNORMAL);
#elif defined(__APPLE__)
  snprintf(full, sizeof(full), "%s/%s", cwd, rel);
  char cmd[4096];
  snprintf(cmd, sizeof(cmd), "open \"%s\"", full);
  system(cmd);
#else
  snprintf(full, sizeof(full), "%s/%s", cwd, rel);
  char cmd[4096];
  snprintf(cmd, sizeof(cmd), "xdg-open \"%s\"", full);
  system(cmd);
#endif
}

static bool draw_button(Font font, Rectangle r, const char *label, bool enabled, float fontSize) {
  Vector2 m = GetMousePosition();
  bool hot = CheckCollisionPointRec(m, r);

  Color bg;
  Color fg = RAYWHITE;

  if (!enabled) bg = (Color){60, 60, 60, 255};
  else if (hot) bg = (Color){70, 120, 200, 255};
  else bg = (Color){40, 90, 170, 255};

  DrawRectangleRounded(r, 0.25f, 10, bg);

  // IMPORTANT: many raylib versions have DrawRectangleRoundedLines(rec, roundness, segments, color)
  DrawRectangleRoundedLines(r, 0.25f, 10, (Color){20, 20, 20, 255});

  Vector2 ts = MeasureTextEx(font, label, fontSize, g_uiSpacing);

  Vector2 pos = {
    r.x + (r.width  - ts.x) * 0.5f,
    r.y + (r.height - ts.y) * 0.5f
  };

  DrawTextEx(font, label, pos, fontSize, g_uiSpacing, fg);

  if (!enabled) return false;
  return hot && IsMouseButtonReleased(MOUSE_LEFT_BUTTON);
}

#ifdef _WIN32
static DWORD WINAPI worker_thread(LPVOID p) {
  (void)p;
  g_running = 1;
  generator_set_log_hook(ui_log_hook);
  g_last_rc = run_generation();
  generator_set_log_hook(NULL);
  g_running = 0;
  return 0;
}
static void start_generation_thread(void) {
  if (g_running) return;
  HANDLE h = CreateThread(NULL, 0, worker_thread, NULL, 0, NULL);
  if (h) CloseHandle(h);
}
#else
static void *worker_thread(void *p) {
  (void)p;
  g_running = 1;
  generator_set_log_hook(ui_log_hook);
  g_last_rc = run_generation();
  generator_set_log_hook(NULL);
  g_running = 0;
  return NULL;
}
static void start_generation_thread(void) {
  if (g_running) return;
  pthread_t t;
  if (pthread_create(&t, NULL, worker_thread, NULL) == 0) pthread_detach(t);
}
#endif

static void draw_log_panel(Font font, Rectangle r) {
  DrawRectangleRec(r, (Color){18, 18, 18, 255});
  DrawRectangleLinesEx(r, 2.0f, (Color){40, 40, 40, 255});

  const float fontSize = 14.0f;
  const int pad = 8;
  const int lineH = 16;

  int maxLines = (int)((r.height - 2*pad) / (float)lineH);
  if (maxLines < 1) maxLines = 1;

  // snapshot log under lock
  char lines[LOG_MAX_LINES][LOG_LINE_MAX];
  int count = 0;

  log_lock();
  count = g_log_count;
  int head = g_log_head;
  for (int i = 0; i < count; i++) {
    int idx = (head - count + i);
    while (idx < 0) idx += LOG_MAX_LINES;
    idx %= LOG_MAX_LINES;
    snprintf(lines[i], LOG_LINE_MAX, "%s", g_log[idx]);
  }
  log_unlock();

  int start = 0;
  if (count > maxLines) start = count - maxLines;

  BeginScissorMode((int)r.x, (int)r.y, (int)r.width, (int)r.height);
  float y = r.y + (float)pad;
  for (int i = start; i < count; i++) {
    DrawTextEx(font, lines[i], (Vector2){r.x + (float)pad, y}, fontSize, g_uiSpacing, (Color){210, 210, 210, 255});
    y += (float)lineH;
  }
  EndScissorMode();
}

int main(void) {
  log_lock_init();

  SetConfigFlags(FLAG_WINDOW_RESIZABLE);
  InitWindow(920, 560, "C-AI Movie Shorts");
  SetTargetFPS(60);

  // Load Inter Regular from resources/
  g_uiFont = LoadFontEx("resources/Inter-Regular.ttf", 64, NULL, 0);
  SetTextureFilter(g_uiFont.texture, TEXTURE_FILTER_BILINEAR);

  while (!WindowShouldClose()) {
    BeginDrawing();
    ClearBackground((Color){25, 25, 25, 255});

    DrawTextEx(g_uiFont, "Folders", (Vector2){30, 20}, 24, g_uiSpacing, RAYWHITE);

    if (draw_button(g_uiFont, (Rectangle){30, 60, 260, 44}, "Open Movies Folder", true, 18)) {
      open_folder_rel("movies");
    }
    if (draw_button(g_uiFont, (Rectangle){30, 115, 260, 44}, "Open Retired Movies Folder", true, 18)) {
      open_folder_rel("movies_retired");
    }
    if (draw_button(g_uiFont, (Rectangle){30, 170, 260, 44}, "Open Output Folder", true, 18)) {
      open_folder_rel("output");
    }
    if (draw_button(g_uiFont, (Rectangle){30, 225, 260, 44}, "Open SRT Folder", true, 18)) {
      open_folder_rel("scripts/srt_files");
    }

    //DrawTextEx(g_uiFont, "Generation", (Vector2){30, 240}, 24, g_uiSpacing, RAYWHITE);

    bool canStart = (g_running == 0);
    const char *startLabel = canStart ? "START GENERATION" : "RUNNING...";
    if (draw_button(g_uiFont, (Rectangle){30, 280, 260, 70}, startLabel, canStart, 22)) {
      // clear UI log before run
      log_lock();
      g_log_head = 0;
      g_log_count = 0;
      log_unlock();

      start_generation_thread();
    }

    char status[256];
    snprintf(status, sizeof(status),
             "Status: %s   (last exit code: %d)",
             (g_running ? "RUNNING" : "IDLE"),
             (int)g_last_rc);
    DrawTextEx(g_uiFont, status, (Vector2){30, 370}, 18, g_uiSpacing, (Color){220, 220, 220, 255});

    DrawTextEx(g_uiFont, "Log", (Vector2){320, 20}, 24, g_uiSpacing, RAYWHITE);
    draw_log_panel(g_uiFont, (Rectangle){320, 60, 570, 470});

    EndDrawing();
  }

  UnloadFont(g_uiFont);
  CloseWindow();
  return 0;
}
