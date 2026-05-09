#include "GifPlayer.h"
#include <gdiplus.h>

using namespace Gdiplus;

GifPlayer::GifPlayer() {}

GifPlayer::~GifPlayer() {
    delete m_image;
}

bool GifPlayer::Load(const std::wstring& filepath) {
    delete m_image;
    m_image = nullptr;
    m_loaded = false;
    m_frameDurations.clear();
    m_currentFrame = 0;

    m_image = Image::FromFile(filepath.c_str());
    if (!m_image || m_image->GetLastStatus() != Ok) {
        delete m_image;
        m_image = nullptr;
        return false;
    }

    m_gifWidth = m_image->GetWidth();
    m_gifHeight = m_image->GetHeight();
    GUID guid;
    m_image->GetFrameDimensionsList(&guid, 1);
    m_frameCount = m_image->GetFrameCount(&guid);
    ExtractFrameDurations();
    m_loaded = true;
    return true;
}

void GifPlayer::ExtractFrameDurations() {
    m_frameDurations.clear();
    UINT count = 0;
    UINT size = 0;
    size = m_image->GetPropertyItemSize(PropertyTagFrameDelay);
    if (size > 0) {
        auto* prop = (PropertyItem*)malloc(size);
        if (m_image->GetPropertyItem(PropertyTagFrameDelay, size, prop) == Ok) {
            count = prop->length / sizeof(long);
            auto* delays = (long*)prop->value;
            for (UINT i = 0; i < count; ++i) {
                int ms = delays[i] * 10; // GDI+ stores in 1/100 seconds
                if (ms < 20) ms = 100;
                m_frameDurations.push_back(ms);
            }
        }
        free(prop);
    }
    // Fallback: if no durations found, use 100ms per frame
    while (m_frameDurations.size() < m_frameCount) {
        m_frameDurations.push_back(100);
    }
}

void GifPlayer::SetSize(int size) {
    m_displaySize = size;
}

int GifPlayer::GetFrameDelay(int index) const {
    if (index < 0 || index >= (int)m_frameDurations.size())
        return 100;
    return m_frameDurations[index];
}

bool GifPlayer::GetFrame(HBITMAP& outBitmap, int& outWidth, int& outHeight) {
    if (!m_loaded || !m_image) return false;

    GUID guid;
    m_image->GetFrameDimensionsList(&guid, 1);
    if (m_currentFrame >= (int)m_frameCount) m_currentFrame = 0;
    m_image->SelectActiveFrame(&guid, m_currentFrame);

    int w = m_displaySize;
    int h = m_displaySize;

    // Create a temporary bitmap to render the frame
    Bitmap frameBmp(w, h, PixelFormat32bppARGB);
    Graphics graphics(&frameBmp);
    graphics.SetCompositingMode(CompositingModeSourceOver);
    graphics.SetInterpolationMode(InterpolationModeNearestNeighbor);
    graphics.Clear(Color(0, 0, 0, 0)); // transparent background

    // Draw the GIF frame scaled to display size
    Rect destRect(0, 0, w, h);
    graphics.DrawImage(m_image, destRect, 0, 0, m_gifWidth, m_gifHeight, UnitPixel);

    HBITMAP hBitmap = CreateDIBSectionFromGdiplusBitmap(&frameBmp);
    if (!hBitmap) return false;

    outBitmap = hBitmap;
    outWidth = w;
    outHeight = h;
    return true;
}

HBITMAP GifPlayer::CreateDIBSectionFromGdiplusBitmap(Bitmap* bmp) const {
    HBITMAP hBitmap = NULL;
    bmp->GetHBITMAP(Color(0, 0, 0, 0), &hBitmap);
    return hBitmap;
}
