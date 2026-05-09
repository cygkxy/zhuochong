#ifndef UNICODE
#define UNICODE
#endif
#include "PetWindow.h"
#include <windowsx.h>
#include <dwmapi.h>
#pragma comment(lib, "dwmapi")
#pragma comment(lib, "gdiplus")

const wchar_t* GifNames[GifNames_SIZE] = {
    L"9ff6d968-515e-42d3-b3e8-0fa54e561312.gif",
    L"1f3c78a7-319c-459a-81e9-5be86107a97f.gif",
    L"b84baff2-2633-4166-9714-b72379e3083a.gif",
    L"26da6319-8f17-49dd-b9b1-55a5d71fe8e0.gif",
    L"c710dac8-ad27-4576-b44e-894a027caa4b.gif",
    L"dedb12c9-382c-49d1-b66f-a93c12e1e156.gif",
    L"9b3a8d8a-d058-48be-834b-034dd5d2e973.gif",
    L"cd5e44f9-7ee3-444a-af04-c96ccb3c8883.gif",
    L"9f843a6a-b9f6-4b05-82b3-56b1e9081daa.gif",
    L"45944575-ffc6-4c73-ab6f-860be5ca651d.gif",
    L"0683881c-9c54-4f89-8889-466473131750.gif",
    L"a195e75c-7df4-49ae-b932-f4bafacc5aa0.gif",
    L"3a22e361-7db2-4b45-a6d5-ff4d90083fe4.gif",
    L"0677e6b6-9057-44b1-8c4b-daff5fc9838b.gif",
    L"3c4d0ed3-f4fc-42fa-bf9f-dbd5390528e9.gif",
    L"8e93cedd-fdae-4a3a-8a55-08e0be2ecd99.gif",
    L"dd12ff56-c349-4714-98ae-5f01e45870dd.gif",
    L"0a3579d1-9a99-4161-a618-709a2029de8c.gif",
    L"09a2fd86-af4a-4ee9-a126-ec9f0bb223d8.gif",
    L"0290e42b-e1d6-4f98-8b9a-43bc77e50310.gif",
    L"929539e9-2f88-40be-82f9-a98b54d3e641.gif",
    L"4289eeb3-ff65-4a4f-a26b-bc8044f6f7c4.gif",
    L"616b7566-b567-4f64-825a-99842114eceb.gif",
    L"d5c20993-c4c5-4bc3-bedc-9668fecd049c.gif",
};

const wchar_t* StateLabels[GifNames_SIZE] = {
    L"开心", L"微笑", L"眨眼", L"期待",
    L"发呆", L"惊喜", L"得意", L"卖萌",
    L"害羞", L"思考", L"打哈欠", L"犯困",
    L"兴奋", L"跳舞", L"唱歌", L"转圈",
    L"跑步", L"走路", L"跳跃", L"蹲下",
    L"招手", L"点赞", L"比心", L"飞吻",
};

// Forward declaration of WindowProc
static LRESULT CALLBACK WindowProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

PetWindow::PetWindow(HINSTANCE hInstance)
    : m_hInst(hInstance) {
    m_configPath = L"pet_config.json";
    LoadConfig();
}

PetWindow::~PetWindow() {
    StopAnimation();
    if (m_hdcMem) DeleteDC(m_hdcMem);
    if (m_hBitmap) DeleteObject(m_hBitmap);
}

bool PetWindow::Create() {
    const wchar_t CLASS_NAME[] = L"RainbowPetWindow";

    WNDCLASS wc = {};
    wc.lpfnWndProc = ::WindowProc;
    wc.hInstance = m_hInst;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = NULL;

    RegisterClass(&wc);

    m_hWnd = CreateWindowEx(
        WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TRANSPARENT,
        CLASS_NAME, L"Rainbow 桌宠",
        WS_POPUP,
        CW_USEDEFAULT, CW_USEDEFAULT,
        WINDOW_SIZE, WINDOW_SIZE,
        NULL, NULL, m_hInst, this
    );

    if (!m_hWnd) return false;

    // Center window
    RECT rc;
    GetWindowRect(m_hWnd, &rc);
    int sw = GetSystemMetrics(SM_CXSCREEN);
    int sh = GetSystemMetrics(SM_CYSCREEN);
    int x = (sw - WINDOW_SIZE) / 2;
    int y = (sh - WINDOW_SIZE) / 2;
    SetWindowPos(m_hWnd, NULL, x, y, WINDOW_SIZE, WINDOW_SIZE, SWP_NOZORDER);

    // Create memory DC
    HDC hdc = GetDC(m_hWnd);
    m_hdcMem = CreateCompatibleDC(hdc);
    ReleaseDC(m_hWnd, hdc);

    // Load first GIF and start animation
    LoadGif(0);

    return true;
}

void PetWindow::Show(int nCmdShow) {
    ShowWindow(m_hWnd, nCmdShow);
}

void PetWindow::Destroy() {
    StopAnimation();
    DestroyWindow(m_hWnd);
}

bool PetWindow::LoadConfig() {
    m_config = PetConfig::load(m_configPath);
    return true;
}

void PetWindow::SaveConfig() {
    m_config.save(m_configPath);
}

void PetWindow::LoadGifList() {
    // Find all GIFs in current directory
    WIN32_FIND_DATA findData;
    HANDLE hFind = FindFirstFile(L"*.gif", &findData);
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            m_gifFiles.push_back(findData.cFileName);
        } while (FindNextFile(hFind, &findData));
        FindClose(hFind);
    }
}

void PetWindow::LoadGif(int idx) {
    if (idx < 0) idx = GifNames_SIZE - 1;
    if (idx >= GifNames_SIZE) idx = 0;
    m_currentGifIdx = idx;

    std::wstring path = GifNames[idx];
    if (!m_gifPlayer.Load(path)) {
        // Try with full path
        wchar_t modulePath[MAX_PATH];
        GetModuleFileName(NULL, modulePath, MAX_PATH);
        std::wstring dir = modulePath;
        auto pos = dir.find_last_of(L"\\/");
        if (pos != std::wstring::npos) {
            dir = dir.substr(0, pos + 1);
            m_gifPlayer.Load(dir + path);
        }
    }

    if (m_gifPlayer.IsLoaded()) {
        m_gifPlayer.SetSize(m_config.size);
        StartAnimation();
        RenderCurrentFrame();
    }
}

void PetWindow::StartAnimation() {
    StopAnimation();
    if (m_gifPlayer.IsLoaded() && m_gifPlayer.GetFrameCount() > 1) {
        int delay = m_gifPlayer.GetFrameDelay(0);
        m_animTimer = SetTimer(m_hWnd, 1, delay, NULL);
    }
}

void PetWindow::StopAnimation() {
    if (m_animTimer) {
        KillTimer(m_hWnd, m_animTimer);
        m_animTimer = 0;
    }
    if (m_autoSwitchTimer) {
        KillTimer(m_hWnd, m_autoSwitchTimer);
        m_autoSwitchTimer = 0;
    }
}

void PetWindow::RenderCurrentFrame() {
    if (!m_gifPlayer.IsLoaded()) return;

    HBITMAP hFrame = NULL;
    int w, h;
    if (!m_gifPlayer.GetFrame(hFrame, w, h)) return;

    // Set up blend function for UpdateLayeredWindow
    HDC hdcScreen = GetDC(NULL);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);
    HBITMAP hOldBmp = (HBITMAP)SelectObject(hdcMem, hFrame);

    POINT pt = { 0, 0 };
    SIZE size = { w, h };
    BLENDFUNCTION blend = {};
    blend.BlendOp = AC_SRC_OVER;
    blend.SourceConstantAlpha = 255;
    blend.AlphaFormat = AC_SRC_ALPHA;

    UpdateLayeredWindow(m_hWnd, hdcScreen, NULL, &size, hdcMem, &pt, 0, &blend, ULW_ALPHA);

    SelectObject(hdcMem, hOldBmp);
    DeleteDC(hdcMem);
    ReleaseDC(NULL, hdcScreen);
    DeleteObject(hFrame);
}

void PetWindow::ShowContextMenu(int x, int y) {
    HMENU hMenu = CreatePopupMenu();
    AppendMenuW(hMenu, MF_STRING, 1001, L"散步模式");
    AppendMenuW(hMenu, MF_STRING, 1002, L"跟随鼠标");
    AppendMenuW(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenuW(hMenu, MF_STRING, 1003, L"对话");
    AppendMenuW(hMenu, MF_STRING, 1004, L"切换动作");
    AppendMenuW(hMenu, MF_STRING, 1005, L"随机表情");
    AppendMenuW(hMenu, MF_STRING, 1006, L"设为主形象");
    AppendMenuW(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenuW(hMenu, MF_STRING, 1007, L"设置");
    AppendMenuW(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenuW(hMenu, MF_STRING, 1008, L"退出");

    SetForegroundWindow(m_hWnd);
    int cmd = TrackPopupMenu(hMenu, TPM_RETURNCMD | TPM_NONOTIFY, x, y, 0, m_hWnd, NULL);
    DestroyMenu(hMenu);

    switch (cmd) {
        case 1001: break; // TBD: toggle walk
        case 1002: break; // TBD: toggle follow
        case 1003: break; // TBD: show chat
        case 1004: LoadGif(m_currentGifIdx + 1); break;
        case 1005: LoadGif(rand() % GifNames_SIZE); break;
        case 1006:
            m_config.mainGif = m_currentGifIdx;
            SaveConfig();
            break;
        case 1007: break; // TBD: settings dialog
        case 1008: PostQuitMessage(0); break;
    }
}

LRESULT PetWindow::HandleMessage(UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_TIMER: {
            if (wParam == 1) {
                // Animation timer - advance to next frame
                m_gifPlayer.NextFrame();
                RenderCurrentFrame();
                int delay = m_gifPlayer.GetFrameDelay(m_gifPlayer.GetCurrentIndex());
                KillTimer(m_hWnd, 1);
                m_animTimer = SetTimer(m_hWnd, 1, delay, NULL);
            }
            return 0;
        }

        case WM_NCHITTEST: {
            LRESULT result = DefWindowProc(m_hWnd, msg, wParam, lParam);
            if (result == HTCLIENT) return HTCAPTION;
            return result;
        }

        case WM_CONTEXTMENU:
            ShowContextMenu(GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam));
            return 0;

        case WM_KEYDOWN:
            if (wParam == VK_LEFT) LoadGif(m_currentGifIdx - 1);
            else if (wParam == VK_RIGHT) LoadGif(m_currentGifIdx + 1);
            else if (wParam == VK_SPACE) LoadGif(rand() % GifNames_SIZE);
            else if (wParam == 'W') {} // TBD: toggle walk
            else if (wParam == 'S') {} // TBD: settings
            else if (wParam == 'C') {} // TBD: chat
            return 0;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProc(m_hWnd, msg, wParam, lParam);
}

static LRESULT CALLBACK WindowProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    PetWindow* pWindow = NULL;
    if (msg == WM_NCCREATE) {
        auto* create = (CREATESTRUCT*)lParam;
        pWindow = (PetWindow*)create->lpCreateParams;
        SetWindowLongPtr(hWnd, GWLP_USERDATA, (LONG_PTR)pWindow);
    } else {
        pWindow = (PetWindow*)GetWindowLongPtr(hWnd, GWLP_USERDATA);
    }
    if (pWindow) return pWindow->HandleMessage(msg, wParam, lParam);
    return DefWindowProc(hWnd, msg, wParam, lParam);
}
