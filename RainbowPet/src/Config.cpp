#include "Config.h"
#include <windows.h>

static std::string ws2s(const std::wstring& ws) {
    if (ws.empty()) return {};
    int len = WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), (int)ws.size(), NULL, 0, NULL, NULL);
    std::string s(len, 0);
    WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), (int)ws.size(), &s[0], len, NULL, NULL);
    return s;
}

json PetConfig::toJson() const {
    return {
        {"size", size},
        {"speed", speed},
        {"auto_walk", autoWalk},
        {"switch_interval", switchInterval},
        {"follow_mouse", followMouse},
        {"main_gif", mainGif},
        {"main_gif_chance", mainGifChance},
        {"bubble_color", bubbleColor},
        {"bubble_text_max", bubbleTextMax},
        {"chat_key", chatKey},
        {"proactive_chat", proactiveChat},
        {"proactive_interval", proactiveInterval},
        {"proactive_random", proactiveRandom},
        {"web_search", webSearch},
        {"api_provider", apiProvider},
        {"api_key", apiKey},
        {"api_model", apiModel},
        {"api_base", apiBase},
        {"api_system_prompt", apiSystemPrompt}
    };
}

PetConfig PetConfig::fromJson(const json& j) {
    PetConfig c;
    if (j.contains("size")) c.size = j["size"];
    if (j.contains("speed")) c.speed = j["speed"];
    if (j.contains("auto_walk")) c.autoWalk = j["auto_walk"];
    if (j.contains("switch_interval")) c.switchInterval = j["switch_interval"];
    if (j.contains("follow_mouse")) c.followMouse = j["follow_mouse"];
    if (j.contains("main_gif")) c.mainGif = j["main_gif"];
    if (j.contains("main_gif_chance")) c.mainGifChance = j["main_gif_chance"];
    if (j.contains("bubble_color")) c.bubbleColor = j["bubble_color"];
    if (j.contains("bubble_text_max")) c.bubbleTextMax = j["bubble_text_max"];
    if (j.contains("chat_key")) c.chatKey = j["chat_key"];
    if (j.contains("proactive_chat")) c.proactiveChat = j["proactive_chat"];
    if (j.contains("proactive_interval")) c.proactiveInterval = j["proactive_interval"];
    if (j.contains("proactive_random")) c.proactiveRandom = j["proactive_random"];
    if (j.contains("web_search")) c.webSearch = j["web_search"];
    if (j.contains("api_provider")) c.apiProvider = j["api_provider"];
    if (j.contains("api_key")) c.apiKey = j["api_key"];
    if (j.contains("api_model")) c.apiModel = j["api_model"];
    if (j.contains("api_base")) c.apiBase = j["api_base"];
    if (j.contains("api_system_prompt")) c.apiSystemPrompt = j["api_system_prompt"];
    return c;
}

void PetConfig::save(const std::wstring& path) {
    std::ofstream file(ws2s(path));
    file << toJson().dump(2);
}

PetConfig PetConfig::load(const std::wstring& path) {
    std::ifstream file(ws2s(path));
    if (!file.is_open()) return PetConfig();
    try {
        json j;
        file >> j;
        return fromJson(j);
    } catch (...) {
        return PetConfig();
    }
}
