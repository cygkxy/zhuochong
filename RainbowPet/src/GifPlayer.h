#pragma once
#include <windows.h>
#include <gdiplus.h>
#include <string>
#include <vector>

#pragma comment(lib, "gdiplus")

class GifPlayer {
public:
    GifPlayer();
    ~GifPlayer();

    bool Load(const std::wstring& filepath);
    void SetSize(int size);
    bool GetFrame(HBITMAP& outBitmap, int& outWidth, int& outHeight);

    int GetFrameCount() const { return (int)m_frameDurations.size(); }
    int GetFrameDelay(int index) const;
    int GetCurrentIndex() const { return m_currentFrame; }
    void SetCurrentIndex(int idx) { m_currentFrame = idx % GetFrameCount(); }
    void NextFrame() { m_currentFrame = (m_currentFrame + 1) % GetFrameCount(); }
    bool IsLoaded() const { return m_loaded; }
    int GetGifWidth() const { return m_gifWidth; }
    int GetGifHeight() const { return m_gifHeight; }

private:
    bool m_loaded = false;
    Gdiplus::Image* m_image = nullptr;
    int m_currentFrame = 0;
    int m_gifWidth = 0;
    int m_gifHeight = 0;
    int m_displaySize = 120;
    std::vector<int> m_frameDurations;
    UINT m_frameCount = 0;

    void ExtractFrameDurations();
    HBITMAP CreateDIBSectionFromGdiplusBitmap(Gdiplus::Bitmap* bmp) const;
};
