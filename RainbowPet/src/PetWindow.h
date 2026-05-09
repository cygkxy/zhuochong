#pragma once
#ifndef UNICODE
#define UNICODE
#define _UNICODE
#endif
#include <windows.h>
#include <string>
#include <vector>
#include "GifPlayer.h"
#include "Config.h"

#define GifNames_SIZE 24

extern const wchar_t* GifNames[GifNames_SIZE];
extern const wchar_t* StateLabels[GifNames_SIZE];

class PetWindow {
public:
    PetWindow(HINSTANCE hInstance);
    ~PetWindow();

    bool Create();
    void Show(int nCmdShow);
    void Destroy();
    HWND GetHWND() const { return m_hWnd; }

    // Window procedure
    LRESULT HandleMessage(UINT msg, WPARAM wParam, LPARAM lParam);

private:
    HINSTANCE m_hInst;
    HWND m_hWnd = NULL;
    HDC m_hdcMem = NULL;
    HBITMAP m_hBitmap = NULL;

    // GIF
    GifPlayer m_gifPlayer;
    int m_currentGifIdx = 0;
    UINT_PTR m_animTimer = 0;
    UINT_PTR m_autoSwitchTimer = 0;

    // Config
    PetConfig m_config;
    std::wstring m_configPath;

    // State
    bool m_isDragging = false;
    int m_dragOffsetX = 0, m_dragOffsetY = 0;

    // Window size
    static const int WINDOW_SIZE = 240;

    bool InitGdiplus();
    void LoadGif(int idx);
    void StartAnimation();
    void StopAnimation();
    void RenderCurrentFrame();
    bool LoadConfig();
    void SaveConfig();
    void ShowContextMenu(int x, int y);

    // GIF file list
    void LoadGifList();
    std::vector<std::wstring> m_gifFiles;
};
