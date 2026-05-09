#pragma once
#include <string>
#include "json.hpp"
#include <fstream>

using json = nlohmann::json;

struct PetConfig {
    // 通用
    int size = 120;
    int speed = 3;
    bool autoWalk = true;
    int switchInterval = 5000;
    bool followMouse = false;
    int mainGif = 0;
    int mainGifChance = 70;

    // 气泡
    std::string bubbleColor = "#2a2a4a";
    int bubbleTextMax = 120;
    std::string chatKey = "c";

    // 主动行为
    bool proactiveChat = false;
    int proactiveInterval = 60;
    bool proactiveRandom = true;
    bool webSearch = false;

    // API
    std::string apiProvider = "deepseek";
    std::string apiKey;
    std::string apiModel = "deepseek-v4-flash";
    std::string apiBase = "https://api.deepseek.com";
    std::string apiSystemPrompt = "你是一个可爱的桌宠，请用简短可爱的语气回复，不超过50个字。";

    json toJson() const;
    static PetConfig fromJson(const json& j);
    void save(const std::wstring& path);
    static PetConfig load(const std::wstring& path);
};
