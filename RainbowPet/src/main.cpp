#include <windows.h>
#include <gdiplus.h>
#include "PetWindow.h"

#pragma comment(lib, "gdiplus")

using namespace Gdiplus;

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int nCmdShow) {
    // Initialize GDI+
    GdiplusStartupInput gdiInput;
    ULONG_PTR gdiToken;
    GdiplusStartup(&gdiToken, &gdiInput, NULL);

    // Create pet window
    PetWindow pet(hInstance);
    if (!pet.Create()) {
        GdiplusShutdown(gdiToken);
        return 1;
    }

    pet.Show(nCmdShow);

    // Message loop
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    // Cleanup
    GdiplusShutdown(gdiToken);
    return 0;
}
