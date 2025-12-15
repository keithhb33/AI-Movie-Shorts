#include "raylib.h"
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "generator.h"
#include "platform_open.h"

#if defined(_WIN32)
  #ifndef WIN32_LEAN_AND_MEAN
  #define WIN32_LEAN_AND_MEAN
  #endif
  #include <windows.h>
#else
  #include <pthread.h>
#endif

typedef struct {
  volatile bool running;
  volatile int  result_code;
#if defined(_WIN32)
  HANDLE thread;
#else
  pthread_t thread;
#endif
} GenState;

static bool UiButton(Rectangle r, const char *label, bool enabled) {
  Vector2 m = GetMousePosition();
  bool hot = enabled && CheckCollisionPointRec(m, r);

  Color fill = enabled ? (hot ? (Color){230,230,230,255} : (Color){210,210,210,255})
                       : (Color){160,160,160,255};
  DrawRectangleRec(r, fill);
  DrawRectangleLinesEx(r, 2, (Color){60,60,60,255});

  int fontSize = 20;
  int tw = MeasureText(label, fontSize);
  DrawText(label,
           (int)(r.x + (r.width - tw)/2),
           (int)(r.y + (r.height - fontSize)/2),
           fontSize,
           (Color){20,20,20,255});

  return hot && IsMouseButtonReleased(MOUSE_LEFT_BUTTON);
}

#if defined(_WIN32)
static DWORD WINAPI GenThreadProc(LPVOID p) {
  GenState *st = (GenState *)p;
  st->result_code = generator_run();
  st->running = false;
  return 0;
}
#else
static void *GenThreadProc(void *p) {
  GenState *st = (GenState *)p;
  st->result_code = generator_run();
  st->running = false;
  return NULL;
}
#endif

static void StartGeneration(GenState *st) {
  if (st->running) return;
  st->running = true;
  st->result_code = 0;

#if defined(_WIN32)
  st->thread = CreateThread(NULL, 0, GenThreadProc, st, 0, NULL);
  if (!st->thread) {
    st->running = false;
    st->result_code = 1;
  }
#else
  if (pthread_create(&st->thread, NULL, GenThreadProc, st) != 0) {
    st->running = false;
    st->result_code = 1;
  }
#endif
}

int main(void) {
  const int W = 820;
  const int H = 420;

  InitWindow(W, H, "C AI Movie Shorts - UI");
  SetTargetFPS(60);

  GenState st = {0};

  while (!WindowShouldClose()) {
    BeginDrawing();
    ClearBackground((Color){245,245,245,255});

    DrawText("C AI Movie Shorts", 24, 18, 28, (Color){25,25,25,255});
    DrawText("Open folders or start generation.", 24, 54, 18, (Color){60,60,60,255});

    bool enabled = !st.running;

    Rectangle b1 = (Rectangle){24, 100, 240, 60};
    Rectangle b2 = (Rectangle){290, 100, 240, 60};
    Rectangle b3 = (Rectangle){556, 100, 240, 60};

    if (UiButton(b1, "Open movies/", enabled)) platform_open_folder("movies");
    if (UiButton(b2, "Open output/", enabled)) platform_open_folder("output");
    if (UiButton(b3, "Open scripts/", enabled)) platform_open_folder("scripts/srt_files");

    // Big start button
    Rectangle start = (Rectangle){24, 200, 772, 120};
    const char *startLabel = st.running ? "Generating... (see terminal output)" : "START GENERATION";
    if (UiButton(start, startLabel, enabled)) {
      StartGeneration(&st);
    }

    // Status line
    char status[256];
    if (st.running) {
      snprintf(status, sizeof(status), "Status: RUNNING");
    } else {
      snprintf(status, sizeof(status), "Status: IDLE (last result code: %d)", (int)st.result_code);
    }
    DrawText(status, 24, 350, 18, (Color){40,40,40,255});

    DrawText("Note: generation logs still print to the terminal.", 24, 378, 16, (Color){80,80,80,255});

    EndDrawing();
  }

  CloseWindow();
  return 0;
}
