#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rainbow 桌宠 - Windows Native Desktop Pet
"""

import os
import sys
import json
import random
import threading
import time
import urllib.request
import urllib.parse
import ssl
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
from collections import deque

# ─── 配置 ─────────────────────────────────────────

def get_base_dir():
    """获取程序所在目录（支持 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_dir():
    """获取资源文件目录（PyInstaller onefile 模式下为临时解压目录）"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return get_base_dir()

BASE_DIR = get_base_dir()
RES_DIR = get_resource_dir()
CONFIG_FILE = os.path.join(BASE_DIR, 'pet_config.json')

DEFAULT_CONFIG = {
    'size': 120,
    'speed': 3,
    'auto_walk': True,
    'switch_interval': 5000,
    'follow_mouse': False,
    # 气泡设置
    'bubble_color': '#2a2a4a',
    'bubble_text_max': 80,
    'chat_key': 'c',
    'proactive_chat': False,
    'proactive_interval': 60,
    'proactive_random': True,
    'web_search': False,
    # API 配置
    'api_provider': 'openai',
    'api_key': '',
    'api_model': 'gpt-4o-mini',
    'api_base': 'https://api.openai.com/v1',
    'api_system_prompt': '你是一个可爱的桌宠，请用简短可爱的语气回复，不超过50个字。',
}

# 所有 GIF 文件（从 Rainbow.md）
GIF_NAMES = [
    "9ff6d968-515e-42d3-b3e8-0fa54e561312.gif",
    "1f3c78a7-319c-459a-81e9-5be86107a97f.gif",
    "b84baff2-2633-4166-9714-b72379e3083a.gif",
    "26da6319-8f17-49dd-b9b1-55a5d71fe8e0.gif",
    "c710dac8-ad27-4576-b44e-894a027caa4b.gif",
    "dedb12c9-382c-49d1-b66f-a93c12e1e156.gif",
    "9b3a8d8a-d058-48be-834b-034dd5d2e973.gif",
    "cd5e44f9-7ee3-444a-af04-c96ccb3c8883.gif",
    "9f843a6a-b9f6-4b05-82b3-56b1e9081daa.gif",
    "45944575-ffc6-4c73-ab6f-860be5ca651d.gif",
    "0683881c-9c54-4f89-8889-466473131750.gif",
    "a195e75c-7df4-49ae-b932-f4bafacc5aa0.gif",
    "3a22e361-7db2-4b45-a6d5-ff4d90083fe4.gif",
    "0677e6b6-9057-44b1-8c4b-daff5fc9838b.gif",
    "3c4d0ed3-f4fc-42fa-bf9f-dbd5390528e9.gif",
    "8e93cedd-fdae-4a3a-8a55-08e0be2ecd99.gif",
    "dd12ff56-c349-4714-98ae-5f01e45870dd.gif",
    "0a3579d1-9a99-4161-a618-709a2029de8c.gif",
    "09a2fd86-af4a-4ee9-a126-ec9f0bb223d8.gif",
    "0290e42b-e1d6-4f98-8b9a-43bc77e50310.gif",
    "929539e9-2f88-40be-82f9-a98b54d3e641.gif",
    "4289eeb3-ff65-4a4f-a26b-bc8044f6f7c4.gif",
    "616b7566-b567-4f64-825a-99842114eceb.gif",
    "d5c20993-c4c5-4bc3-bedc-9668fecd049c.gif",
]

# 状态标签
STATE_LABELS = [
    "开心", "微笑", "眨眼", "期待",
    "发呆", "惊喜", "得意", "卖萌",
    "害羞", "思考", "打哈欠", "犯困",
    "兴奋", "跳舞", "唱歌", "转圈",
    "跑步", "走路", "跳跃", "蹲下",
    "招手", "点赞", "比心", "飞吻",
]

STATE_COLORS = [
    "#FFD700", "#FFB6C1", "#87CEEB", "#98FB98",
    "#DDA0DD", "#FFA500", "#FF69B4", "#FFE4B5",
    "#FFC0CB", "#B0C4DE", "#F0E68C", "#B0E0E6",
    "#FF6347", "#7B68EE", "#00CED1", "#FF1493",
    "#32CD32", "#FFD700", "#FF4500", "#8A2BE2",
    "#00BFFF", "#FFD700", "#FF69B4", "#FFB6C1",
]

SPEECHES = [
    "今天好开心！", "有点困了呢…",
    "你好呀！", "陪我玩~", "嗯…在想事情",
    "哇！", "好无聊啊…", "喜欢！",
    "嘿嘿~", "天气真好~", "想吃点东西…",
    "来追我呀！", "好棒！", "唔…",
    "你好！", "加油！", "休息一下吧",
    "好神奇哦！", "嗯嗯！",
    "好厉害！", "再玩一会儿嘛~",
]

TRANSPARENT_COLOR = "#000001"  # 透明色
WINDOW_SIZE = 240  # 窗口固定尺寸（画布大小）

# ─── 主题色（低对比半透明感） ─────────────────────
THEME = {
    'bg': '#0f111a',
    'surface': '#161b28',
    'surface_hover': '#1c2333',
    'surface_active': '#1e293b',
    'accent': '#22d3ee',
    'accent_hover': '#38e0ff',
    'accent_dark': '#0891b2',
    'accent2': '#7c3aed',
    'accent3': '#06b6d4',
    'text': '#e2e8f0',
    'text_sec': '#8892a8',
    'text_muted': '#3d4a5c',
    'border': '#1a2230',
    'border_light': '#232e3e',
    'input_bg': '#0d1117',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'scrollbar_bg': '#0f111a',
    'scrollbar_fg': '#1a2230',
}


# ─── GIF 帧加载器 ──────────────────────────────

class GifLoader:
    """加载并缓存所有 GIF 的帧"""

    def __init__(self, gif_dir):
        self.gif_dir = gif_dir
        self.cache = {}  # name -> [(PhotoImage, duration), ...]

    def load(self, name, size):
        """加载 GIF，返回 (frames, durations) 元组"""
        if name in self.cache:
            cached_size, frames, durations = self.cache[name]
            if cached_size == size:
                return frames, durations

        path = os.path.join(self.gif_dir, name)
        if not os.path.exists(path):
            return [], []

        try:
            img = Image.open(path)
            frames = []
            durations = []

            for frame in ImageSequence.Iterator(img):
                duration = frame.info.get('duration', 100)
                if duration < 20:
                    duration = 100

                # 缩放
                resized = frame.copy()
                if size != resized.size[0]:
                    resized = resized.resize((size, size), Image.NEAREST)

                # 透明背景处理
                if resized.mode in ('RGBA', 'P'):
                    bg = Image.new('RGBA', resized.size, (0, 0, 1, 255))
                    if resized.mode == 'P':
                        resized = resized.convert('RGBA')
                    bg.paste(resized, (0, 0), resized)
                    resized = bg
                else:
                    resized = resized.convert('RGBA')

                tk_img = ImageTk.PhotoImage(resized)
                frames.append(tk_img)
                durations.append(duration)

            self.cache[name] = (size, frames, durations)
            return frames, durations

        except Exception as e:
            print(f"加载 GIF 失败 {name}: {e}")
            return [], []


# ─── 桌宠主窗口 ──────────────────────────────────

class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rainbow 桌宠")

        # 窗口设置
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', TRANSPARENT_COLOR)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.resizable(False, False)

        # 配置
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        self.size = self.config['size']
        self.speed = self.config['speed']
        self.auto_walk = self.config['auto_walk']
        self.switch_interval = self.config['switch_interval']
        self.follow_mouse = self.config['follow_mouse']
        self.bubble_color = self.config.get('bubble_color', '#2a2a4a')
        self.bubble_text_max = self.config.get('bubble_text_max', 80)
        self.chat_key = self.config.get('chat_key', 'c')
        self.proactive_chat = self.config.get('proactive_chat', False)
        self.proactive_interval = self.config.get('proactive_interval', 60)
        self.proactive_random = self.config.get('proactive_random', True)
        self.web_search = self.config.get('web_search', False)

        # 状态
        self.current_idx = 0
        self.is_dragging = False
        self.is_walking = False
        self.drag_x = 0
        self.drag_y = 0
        self.target_x = None
        self.target_y = None
        self.frame_index = 0
        self.frames = []
        self.durations = []
        self.anim_after = None
        self.speech_after = None
        self.menu_visible = False
        self.settings_visible = False
        self.chat_visible = False
        self.running = True
        self.api_ready = False
        self.chat_history = []
        self._thinking = False
        self._last_bound_key = None
        self._proactive_after = None
        self._proactive_timeout = None

        # 从配置加载 API 设置
        self.api_provider = self.config.get('api_provider', 'openai')
        self.api_key = self.config.get('api_key', '')
        self.api_model = self.config.get('api_model', 'gpt-4o-mini')
        self.api_base = self.config.get('api_base', 'https://api.openai.com/v1')
        self.api_system_prompt = self.config.get('api_system_prompt',
            '你是一个可爱的桌宠，请用简短可爱的语气回复，不超过50个字。')
        if self.api_key:
            self.api_ready = True

        # 加载 GIF
        self.gif_dir = RES_DIR
        self.loader = GifLoader(self.gif_dir)

        # 创建界面
        self._build_ui()

        # 启动动画
        self.switch_gif(0)
        self._start_auto_switch()
        self._start_walk_loop()

        # 窗口位置（屏幕居中）
        self.center_window()

        # 绑定事件
        self._bind_events()

        if self.api_ready and self.proactive_chat:
            self._start_proactive_timer()

        # 关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def _build_ui(self):
        """构建界面"""
        # 主画布（固定大小）
        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_SIZE,
            height=WINDOW_SIZE,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        # 宠物图像（居中）
        self.img_on_canvas = self.canvas.create_image(
            WINDOW_SIZE // 2, WINDOW_SIZE // 2,
            anchor='center',
        )

        # 对话气泡（独立窗口，稍后创建）
        self.speech_win = None

        # 右键菜单（用 Toplevel）
        self._build_context_menu()

        # 设置窗口
        self._build_settings()

    def _build_context_menu(self):
        """构建右键菜单（圆角毛玻璃风格）"""
        self.menu_win = tk.Toplevel(self.root)
        self.menu_win.overrideredirect(True)
        self.menu_win.attributes('-topmost', True)
        self.menu_win.withdraw()

        # 外框
        outer = tk.Frame(self.menu_win, bg=THEME['border'], bd=1, relief='flat')
        outer.pack()
        inner = tk.Frame(outer, bg=THEME['surface'], bd=0)
        inner.pack(padx=1, pady=1, fill='both', expand=True)

        items = [
            ("🚶  散步模式", self.toggle_walk),
            ("👆  跟随鼠标", self.toggle_follow),
            ("💃  跳舞", lambda: self.switch_gif(13)),
            None,  # separator
            ("💬  对话", self.show_chat),
            ("⏭️  切换动作", self.next_anim),
            ("🎲  随机表情", self.random_anim),
            None,
            ("⚙️  设置", self.toggle_settings),
            None,
            ("👋  退出", self.quit),
        ]

        for item in items:
            if item is None:
                sep = tk.Frame(inner, height=1, bg=THEME['border'])
                sep.pack(fill='x', padx=10, pady=3)
            else:
                text, cmd = item
                btn = tk.Label(
                    inner, text=text,
                    fg=THEME['text'], bg=THEME['surface'],
                    font=("Microsoft YaHei", 10),
                    cursor="hand2", padx=18, pady=7, anchor='w',
                )
                btn.pack(fill='x')
                btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=THEME['surface_hover']))
                btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=THEME['surface']))
                btn.bind('<Button-1>', lambda e, c=cmd: self._menu_action(c))

    def _build_settings(self):
        """构建设置面板"""
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.overrideredirect(True)
        self.settings_win.attributes('-topmost', True)
        self.settings_win.withdraw()
        self.settings_win.configure(bg=THEME['border'])

        w, h = 360, 520
        self.settings_win.geometry(f"{w}x{h}")

        # 内容容器
        inner_root = tk.Frame(self.settings_win, bg=THEME['bg'])
        inner_root.pack(fill='both', expand=True, padx=1, pady=1)

        # 标题栏（带关闭按钮）
        title_bar = tk.Frame(inner_root, bg=THEME['bg'])
        title_bar.pack(fill='x', pady=(10, 0))
        tk.Label(title_bar, text="⚙️  桌宠设置",
                 fg=THEME['text'], bg=THEME['bg'],
                 font=("Microsoft YaHei", 14, "bold")).pack(side='left', padx=(16, 0))
        close_btn = tk.Label(title_bar, text="✕", fg=THEME['text_muted'], bg=THEME['bg'],
                              cursor="hand2", font=("Microsoft YaHei", 14), padx=(0, 14))
        close_btn.pack(side='right')
        close_btn.bind('<Enter>', lambda e: close_btn.configure(fg=THEME['text']))
        close_btn.bind('<Leave>', lambda e: close_btn.configure(fg=THEME['text_muted']))
        close_btn.bind('<Button-1>', lambda e: self.toggle_settings())
        # 标题下面的 accent 线
        accent_line = tk.Frame(inner_root, height=2, bg=THEME['accent'])
        accent_line.pack(fill='x', padx=14, pady=(6, 6))

        # 可滚动区域
        scroll_container = tk.Frame(inner_root, bg=THEME['bg'])
        scroll_container.pack(fill='both', expand=True, padx=8)

        scroll_canvas = tk.Canvas(scroll_container, bg=THEME['bg'],
                                   highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(scroll_container, orient='vertical',
                                  command=scroll_canvas.yview,
                                  bg=THEME['scrollbar_bg'],
                                  troughcolor=THEME['scrollbar_bg'],
                                  activebackground=THEME['scrollbar_fg'],
                                  width=10)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll_canvas.pack(side='left', fill='both', expand=True)

        inner_frame = tk.Frame(scroll_canvas, bg=THEME['bg'])
        scroll_canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        def _on_inner_configure(ev):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all'))
        inner_frame.bind('<Configure>', _on_inner_configure)
        def _on_mousewheel(ev):
            scroll_canvas.yview_scroll(-1 * (ev.delta // 120), 'units')
        scroll_canvas.bind('<Enter>', lambda e: scroll_canvas.bind_all('<MouseWheel>', _on_mousewheel))
        scroll_canvas.bind('<Leave>', lambda e: scroll_canvas.unbind_all('<MouseWheel>'))

        def _section_header(text):
            """带顶部分隔线和左侧色条的 section 标题"""
            # 分隔线
            tk.Frame(inner_frame, height=1, bg=THEME['border']).pack(fill='x', pady=(8, 0))
            hdr = tk.Frame(inner_frame, bg=THEME['bg'])
            hdr.pack(fill='x', pady=(6, 4))
            bar = tk.Frame(hdr, width=3, bg=THEME['accent'])
            bar.pack(side='left', fill='y', padx=(8, 6))
            tk.Label(hdr, text=text, fg=THEME['accent'], bg=THEME['bg'],
                     font=("Microsoft YaHei", 10, "bold"), anchor='w').pack(side='left', fill='x')

        def _make_row():
            """创建设置行容器"""
            r = tk.Frame(inner_frame, bg=THEME['surface'])
            r.pack(fill='x', pady=3, padx=6)
            return r

        def _row_label(parent, text, width=7):
            tk.Label(parent, text=text, fg=THEME['text_sec'], bg=THEME['surface'],
                     font=("Microsoft YaHei", 10), width=width, anchor='w').pack(side='left', padx=(12, 4))

        def _value_label(parent, width=3):
            lbl = tk.Label(parent, text='', fg=THEME['text_muted'], bg=THEME['surface'],
                           font=("Microsoft YaHei", 9), width=width, anchor='e')
            lbl.pack(side='right', padx=(0, 10))
            return lbl

        def _styled_entry(parent, var, width=14, **kw):
            """带边框的输入框"""
            ef = tk.Frame(parent, bg=THEME['border_light'], bd=1, relief='flat')
            ef.pack(side='left', fill='x', expand=True, padx=(0, 10))
            entry = tk.Entry(ef, textvariable=var,
                             bg=THEME['input_bg'], fg=THEME['text'], bd=2,
                             font=kw.get('font', ("Microsoft YaHei", 10)),
                             width=width, justify=kw.get('justify', 'left'),
                             insertbackground=THEME['text'],
                             highlightthickness=0, relief='flat')
            entry.pack(fill='x', padx=2, pady=2)
            return entry

        # ─── 通用设置 ───
        _section_header("通用")

        # 大小
        r1 = _make_row()
        _row_label(r1, "大小")
        self.size_var = tk.IntVar(value=self.size)
        s = ttk.Scale(r1, from_=50, to=250, orient='horizontal',
                       variable=self.size_var, command=self._on_resize)
        s.pack(side='left', fill='x', expand=True, padx=(4, 4))
        self.size_label = _value_label(r1)
        self.size_label.configure(text=str(self.size))

        # 速度
        r2 = _make_row()
        _row_label(r2, "速度")
        self.speed_var = tk.IntVar(value=self.speed)
        ttk.Scale(r2, from_=1, to=10, orient='horizontal',
                  variable=self.speed_var, command=self._on_speed).pack(
            side='left', fill='x', expand=True, padx=(4, 4))

        # 自动漫游 + 切换间隔
        r3 = _make_row()
        _row_label(r3, "自动漫游")
        self.walk_var = tk.BooleanVar(value=self.auto_walk)
        cb = tk.Checkbutton(r3, variable=self.walk_var,
                            bg=THEME['surface'], fg=THEME['text'],
                            selectcolor=THEME['bg'],
                            activebackground=THEME['surface'],
                            command=self._on_auto_walk)
        cb.pack(side='left', padx=(4, 0))

        r4 = _make_row()
        _row_label(r4, "切换间隔")
        self.interval_var = tk.StringVar(value=str(self.switch_interval // 1000))
        intervals = ["3秒", "5秒", "8秒", "15秒"]
        menu = ttk.Combobox(r4, values=intervals,
                            state='readonly', width=10)
        menu.current(1)
        menu.bind('<<ComboboxSelected>>',
                  lambda e: self._on_interval(menu.get()))
        menu.pack(side='left', padx=(4, 0))

        # ─── 气泡 ───
        _section_header("气泡")

        # 气泡颜色（色块选择）
        r5 = _make_row()
        _row_label(r5, "颜色")
        colors = {"紫色": "#2a2a4a", "蓝色": "#1a3a6a", "绿色": "#1a4a2a",
                  "红色": "#5a2a2a", "粉色": "#5a2a4a", "橙色": "#5a3a1a",
                  "青色": "#1a4a4a", "深灰": "#333333"}
        current_color_name = "紫色"
        for name, code in colors.items():
            if code == self.bubble_color:
                current_color_name = name
                break
        # 当前选中的颜色名（用于 hover 提示）
        self._bubble_sel_name = current_color_name
        # 色块行
        swatch_row = tk.Frame(r5, bg=THEME['surface'])
        swatch_row.pack(side='left', fill='x', expand=True, padx=(4, 8))
        for cname, chex in colors.items():
            is_active = (cname == current_color_name)
            outer = tk.Frame(swatch_row, bg=THEME['accent'] if is_active else THEME['surface'],
                             bd=0, relief='flat')
            outer.pack(side='left', padx=2)
            chip = tk.Frame(outer, bg=chex, width=20, height=20, bd=0, relief='flat')
            chip.pack(padx=2, pady=2)
            chip.bind('<Button-1>', lambda e, n=cname, h=chex: self._on_pick_color(n, h))
            chip.bind('<Enter>', lambda e, n=cname, o=outer: o.configure(bg=THEME['accent']))
            chip.bind('<Leave>', lambda e, n=cname, o=outer, act=is_active:
                      o.configure(bg=THEME['accent'] if act else THEME['surface']))
            if is_active:
                # 选中标记
                tk.Label(outer, text="✓", fg='white', bg=chex,
                         font=("Microsoft YaHei", 8)).pack(padx=2, pady=0)

        self.bubble_color_var = tk.StringVar(value=current_color_name)
        self.color_preview = tk.Canvas(r5, width=18, height=18,
                                        bg=colors[current_color_name],
                                        highlightthickness=0, bd=0)
        self.color_preview.pack(side='left', padx=(0, 8))

        # 气泡字数
        r6 = _make_row()
        _row_label(r6, "最大字数")
        self.bubble_len_var = tk.IntVar(value=self.bubble_text_max)
        def on_len_change(val):
            v = int(float(val))
            self.bubble_len_label.configure(text=str(v))
            self.bubble_text_max = v
            self.config['bubble_text_max'] = v
            self.save_config()
        len_scale = ttk.Scale(r6, from_=20, to=200, orient='horizontal',
                              variable=self.bubble_len_var, command=on_len_change)
        len_scale.pack(side='left', fill='x', expand=True, padx=(4, 4))
        self.bubble_len_label = _value_label(r6)
        self.bubble_len_label.configure(text=str(self.bubble_text_max))

        # 对话快捷键
        r7 = _make_row()
        _row_label(r7, "快捷键")
        key_ef = tk.Frame(r7, bg=THEME['border_light'], bd=1, relief='flat')
        key_ef.pack(side='left', padx=(4, 0))
        self.chat_key_var = tk.StringVar(value=self.chat_key)
        key_entry = tk.Entry(key_ef, textvariable=self.chat_key_var,
                             bg=THEME['input_bg'], fg=THEME['text'], bd=0,
                             font=("Microsoft YaHei", 12, "bold"),
                             width=3, justify='center',
                             insertbackground=THEME['text'])
        key_entry.pack(padx=2, pady=2)
        tk.Label(r7, text="（按一个键）", fg=THEME['text_muted'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 9)).pack(side='left', padx=(6, 0))

        # ─── 自主行为 ───
        _section_header("自主行为")

        # 主动说话
        r8 = _make_row()
        _row_label(r8, "主动说话")
        self.proactive_var = tk.BooleanVar(value=self.proactive_chat)
        cb_pc = tk.Checkbutton(r8, variable=self.proactive_var,
                               bg=THEME['surface'], fg=THEME['text'],
                               selectcolor=THEME['bg'],
                               activebackground=THEME['surface'],
                               command=self._on_proactive_toggle)
        cb_pc.pack(side='left', padx=(4, 0))
        # 模式选择
        self.proactive_rand_var = tk.BooleanVar(value=self.proactive_random)
        cb_rand = tk.Checkbutton(r8, variable=self.proactive_rand_var,
                                 bg=THEME['surface'], fg=THEME['text'],
                                 selectcolor=THEME['bg'],
                                 activebackground=THEME['surface'],
                                 command=self._on_proactive_rand_toggle)
        cb_rand.pack(side='left', padx=(2, 0))
        tk.Label(r8, text="随机", fg=THEME['text_muted'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 9)).pack(side='left')
        tk.Label(r8, text="定时间隔", fg=THEME['text_muted'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 9)).pack(side='left', padx=(14, 4))
        int_ef = tk.Frame(r8, bg=THEME['border_light'], bd=1, relief='flat')
        int_ef.pack(side='left')
        self.proactive_int_var = tk.IntVar(value=self.proactive_interval)
        tk.Entry(int_ef, textvariable=self.proactive_int_var,
                 bg=THEME['input_bg'], fg=THEME['text'], bd=0,
                 font=("Microsoft YaHei", 10),
                 width=4, justify='center',
                 insertbackground=THEME['text']).pack(padx=2, pady=2)
        tk.Label(r8, text="秒", fg=THEME['text_muted'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 9)).pack(side='left', padx=(4, 0))

        # 联网搜索
        r9 = _make_row()
        _row_label(r9, "联网搜索")
        self.search_var = tk.BooleanVar(value=self.web_search)
        cb_ws = tk.Checkbutton(r9, variable=self.search_var,
                               bg=THEME['surface'], fg=THEME['text'],
                               selectcolor=THEME['bg'],
                               activebackground=THEME['surface'],
                               command=self._on_search_toggle)
        cb_ws.pack(side='left', padx=(4, 0))
        tk.Label(r9, text="（对话时自动搜索参考）", fg=THEME['text_muted'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 9)).pack(side='left', padx=(6, 0))

        # ─── AI 对话 ───
        _section_header("AI 对话")

        # Provider
        r10 = _make_row()
        _row_label(r10, "提供方")
        self.api_provider_var = tk.StringVar(value=self.api_provider)
        provider_menu = ttk.Combobox(r10, textvariable=self.api_provider_var,
                                     values=["openai", "claude", "deepseek", "自定义"],
                                     state='readonly', width=12)
        provider_menu.pack(side='left', padx=(4, 4))
        provider_menu.bind('<<ComboboxSelected>>', self._on_provider_change)

        # API Key
        r11 = _make_row()
        _row_label(r11, "API Key")
        self.api_key_var = tk.StringVar(value=self.api_key)
        key_ef2 = tk.Frame(r11, bg=THEME['border_light'], bd=1, relief='flat')
        key_ef2.pack(side='left', fill='x', expand=True, padx=(4, 0))
        self.api_key_entry = tk.Entry(key_ef2, textvariable=self.api_key_var,
                                       bg=THEME['input_bg'], fg=THEME['text'], bd=0,
                                       font=("Microsoft YaHei", 10), width=20,
                                       show='*', insertbackground=THEME['text'])
        self.api_key_entry.pack(fill='x', padx=2, pady=2)
        # 显隐按钮放 API Key 这行右侧
        self.key_show_btn = tk.Label(r11, text="👁", fg=THEME['text_muted'], bg=THEME['surface'],
                                      cursor="hand2", font=("Microsoft YaHei", 12))
        self.key_show_btn.pack(side='right', padx=(0, 10))
        self._key_hidden = True
        self.key_show_btn.bind('<ButtonPress-1>', lambda e: self._toggle_key_show())
        self.key_show_btn.bind('<ButtonRelease-1>', lambda e: self._toggle_key_show())

        # Model
        r12 = _make_row()
        _row_label(r12, "模型")
        self.api_model_var = tk.StringVar(value=self.api_model)
        _styled_entry(r12, self.api_model_var)

        # Base URL
        r13 = _make_row()
        _row_label(r13, "接口地址", width=7)
        self.api_base_var = tk.StringVar(value=self.api_base)
        _styled_entry(r13, self.api_base_var, font=("Microsoft YaHei", 9))

        # 系统提示
        r14 = _make_row()
        _row_label(r14, "人格设定")
        self.api_sp_var = tk.StringVar(value=self.api_system_prompt)
        _styled_entry(r14, self.api_sp_var, font=("Microsoft YaHei", 9))

        # 保存按钮（全宽）
        btn_outer = tk.Frame(inner_frame, bg=THEME['bg'])
        btn_outer.pack(fill='x', pady=(12, 4), padx=12)
        save_btn = tk.Label(
            btn_outer, text="💾  保存 API 设置",
            fg=THEME['text'], bg=THEME['accent_dark'], cursor="hand2",
            font=("Microsoft YaHei", 11), padx=0, pady=8,
        )
        save_btn.pack(fill='x')
        save_btn.bind('<Enter>', lambda e: save_btn.configure(bg=THEME['accent']))
        save_btn.bind('<Leave>', lambda e: save_btn.configure(bg=THEME['accent_dark']))
        save_btn.bind('<Button-1>', lambda e: self._save_api_settings())

        # 状态标签
        self.api_status_label = tk.Label(inner_frame, text="", fg=THEME['success'],
                                          bg=THEME['bg'],
                                          font=("Microsoft YaHei", 9))
        self.api_status_label.pack(pady=(2, 6))

        # 绑定 ESC 关闭
        self.root.bind('<Escape>', lambda e: self._close_settings())

    # ─── 核心功能 ────────────────────────────────

    def switch_gif(self, idx, force=False):
        """切换到指定 GIF 动画"""
        if idx < 0:
            idx = len(GIF_NAMES) - 1
        elif idx >= len(GIF_NAMES):
            idx = 0

        if idx == self.current_idx and not force:
            return

        self.current_idx = idx
        name = GIF_NAMES[idx]

        # 加载帧
        frames, durations = self.loader.load(name, self.size)
        if not frames:
            return

        self.frames = frames
        self.durations = durations
        self.frame_index = 0

        # 更新状态标签
        # 更新状态颜色
        color = STATE_COLORS[idx % len(STATE_COLORS)]

        # 播放第一帧
        self._play_frame()

    def _play_frame(self):
        """播放当前帧并调度下一帧"""
        if not self.frames:
            return

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.canvas.itemconfig(self.img_on_canvas, image=self.frames[self.frame_index])
        dur = self.durations[self.frame_index] if self.frame_index < len(self.durations) else 100

        self.frame_index += 1
        self.anim_after = self.root.after(dur, self._play_frame)

    def next_anim(self):
        """下一个动画"""
        self.switch_gif(self.current_idx + 1)

    def prev_anim(self):
        """上一个动画"""
        self.switch_gif(self.current_idx - 1)

    def random_anim(self):
        """随机动画"""
        idx = random.randint(0, len(GIF_NAMES) - 1)
        self.switch_gif(idx)

    def say(self, text):
        """显示对话气泡（独立窗口，位于宠物上方）"""
        # 关闭旧气泡
        self._hide_speech()

        # 空内容不显示
        if not text or not text.strip():
            return

        # 过长文本截断
        max_len = self.bubble_text_max
        if len(text) > max_len:
            text = text[:max_len-3] + '...'

        # 创建气泡窗口
        self.speech_win = tk.Toplevel(self.root)
        self.speech_win.overrideredirect(True)
        self.speech_win.attributes('-topmost', True)
        self.speech_win.configure(bg=THEME['bg'])

        # 气泡主体
        border_frame = tk.Frame(self.speech_win, bg=THEME['border'], bd=0)
        border_frame.pack(padx=2, pady=(2, 0))
        bubble_body = tk.Frame(border_frame, bg=self.bubble_color, bd=0)
        bubble_body.pack(padx=1, pady=1)
        label = tk.Label(
            bubble_body, text=text,
            fg='white', bg=self.bubble_color,
            font=("Microsoft YaHei", 10),
            wraplength=220,
            padx=14, pady=8,
        )
        label.pack()

        # 小三角尾巴
        tail = tk.Label(
            self.speech_win, text="▼",
            fg=self.bubble_color, bg=THEME['bg'],
            font=("Microsoft YaHei", 10),
        )
        tail.pack(pady=(0, 0))

        # 计算尺寸
        self.speech_win.update_idletasks()
        w = self.speech_win.winfo_reqwidth()
        h = self.speech_win.winfo_reqheight()

        # 定位：宠物图片正上方居中（跟随图片大小）
        px = self.root.winfo_x()
        py = self.root.winfo_y()
        img_top = py + (WINDOW_SIZE - self.size) // 2  # 图片顶部在屏幕上的 y

        bx = px + (WINDOW_SIZE - w) // 2
        by = img_top - h - 5  # 图片顶部往上偏移

        # 不超出屏幕边界
        sw = self.root.winfo_screenwidth()
        bx = max(4, min(bx, sw - w - 4))
        if by < 0:
            by = 0

        self.speech_win.geometry(f"+{bx}+{by}")

        # 自动隐藏
        if self.speech_after:
            self.root.after_cancel(self.speech_after)
        self.speech_after = self.root.after(4000, self._hide_speech)

    def _hide_speech(self):
        """隐藏对话气泡"""
        if self.speech_after:
            self.root.after_cancel(self.speech_after)
            self.speech_after = None
        if self.speech_win and self.speech_win.winfo_exists():
            self.speech_win.destroy()
        self.speech_win = None

    def _update_speech_position(self):
        """气泡跟随宠物移动和大小"""
        if not self.speech_win or not self.speech_win.winfo_exists():
            return
        w = self.speech_win.winfo_reqwidth()
        h = self.speech_win.winfo_reqheight()
        px = self.root.winfo_x()
        py = self.root.winfo_y()
        img_top = py + (WINDOW_SIZE - self.size) // 2
        bx = px + (WINDOW_SIZE - w) // 2
        by = img_top - h - 5
        sw = self.root.winfo_screenwidth()
        bx = max(4, min(bx, sw - w - 4))
        if by < 0:
            by = 0
        self.speech_win.geometry(f"+{bx}+{by}")

    def random_speak(self):
        """随机说话（低概率触发，避免刷屏）"""
        if random.random() > 0.06:
            return
        text = random.choice(SPEECHES)
        self.say(text)

    # ─── 窗口操作 ────────────────────────────────

    def center_window(self):
        """居中显示"""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - WINDOW_SIZE) // 2
        y = (sh - WINDOW_SIZE) // 2
        self.root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}+{x}+{y}")

    def _resize_window(self, new_size):
        """调整图片大小（窗口固定）"""
        self.size = new_size
        # 重新加载当前 GIF（self.size 控制图片缩放）
        self.switch_gif(self.current_idx, force=True)

    # ─── 动画切换定时器 ──────────────────────────

    def _start_auto_switch(self):
        """启动自动切换动画"""
        self._auto_switch_running = True
        self._do_auto_switch()

    def _do_auto_switch(self):
        if not getattr(self, '_auto_switch_running', False):
            return
        # 不切换太频繁
        self.next_anim()
        self.root.after(self.switch_interval, self._do_auto_switch)

    def stop_auto_switch(self):
        self._auto_switch_running = False

    # ─── 漫游逻辑 ────────────────────────────────

    def _start_walk_loop(self):
        """启动移动循环"""
        self._walk_loop_running = True
        self._do_walk_loop()

    def _do_walk_loop(self):
        if not getattr(self, '_walk_loop_running', False):
            return

        if not self.is_dragging:
            if self.follow_mouse:
                self._do_follow_mouse()
            elif self.is_walking:
                self._do_walk_to_target()
            elif self.auto_walk and random.random() > 0.97:
                self._do_random_walk()

        # 气泡跟随宠物移动
        self._update_speech_position()

        self.root.after(50, self._do_walk_loop)

    def _do_random_walk(self):
        """随机移动一小步"""
        dx = random.randint(-self.speed * 3, self.speed * 3)
        dy = random.randint(-self.speed * 3, self.speed * 3)
        self._move_by(dx, dy)

    def _do_walk_to_target(self):
        """走到目标位置"""
        if self.target_x is None:
            self._pick_new_target()
            return

        wx = self.root.winfo_x()
        wy = self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        # 在屏幕边缘时换目标
        at_left = wx <= 0
        at_right = wx >= sw - WINDOW_SIZE
        at_top = wy <= 0
        at_bottom = wy >= sh - WINDOW_SIZE

        cx = wx + WINDOW_SIZE // 2
        cy = wy + WINDOW_SIZE // 2
        dx = self.target_x - cx
        dy = self.target_y - cy

        # 目标在屏幕外方向时重新选
        if (at_left and dx < 0) or (at_right and dx > 0) or \
           (at_top and dy < 0) or (at_bottom and dy > 0):
            self._pick_new_target()
            return

        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 10:
            self._pick_new_target()
            return

        step = min(self.speed * 2, dist)
        self._move_by(dx / dist * step, dy / dist * step)

    def _do_follow_mouse(self):
        """跟随鼠标（使用全局鼠标位置）"""
        try:
            mx, my = self.root.winfo_pointerxy()
        except:
            return

        wx = self.root.winfo_x()
        wy = self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        # 在屏幕边缘时停止跟随
        if wx <= 0 or wx >= sw - WINDOW_SIZE or wy <= 0 or wy >= sh - WINDOW_SIZE:
            return

        cx = wx + WINDOW_SIZE // 2
        cy = wy + WINDOW_SIZE // 2
        dx = mx - cx
        dy = my - cy
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 30:
            return

        step = min(self.speed * 2, dist)
        self._move_by(dx / dist * step, dy / dist * step)

    def _pick_new_target(self):
        """选择新的散步目标"""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.target_x = random.randint(50, sw - 50)
        self.target_y = random.randint(50, sh - 100)

    def _move_by(self, dx, dy):
        """相对移动，带边界检查"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        nx = max(0, min(sw - WINDOW_SIZE, x + dx))
        ny = max(0, min(sh - WINDOW_SIZE, y + dy))
        self.root.geometry(f"+{int(nx)}+{int(ny)}")

    def toggle_walk(self):
        """切换散步模式"""
        self.is_walking = not self.is_walking
        if self.is_walking:
            self.follow_mouse = False
            self._pick_new_target()
            self.say("去散步啦~ 🚶")
            # 切换到走路动画
            self.switch_gif(17)
        else:
            self.say("不走了~")

    def toggle_follow(self):
        """切换跟随鼠标"""
        self.follow_mouse = not self.follow_mouse
        if self.follow_mouse:
            self.is_walking = False
            self.say("跟着你~ 👆")
        else:
            self.say("好哒~")

    # ─── 事件绑定 ────────────────────────────────

    def _bind_events(self):
        """绑定所有事件"""
        # 拖拽
        self.canvas.bind('<ButtonPress-1>', self._on_drag_start)
        self.canvas.bind('<B1-Motion>', self._on_drag_move)
        self.canvas.bind('<ButtonRelease-1>', self._on_drag_end)

        # 右键
        self.canvas.bind('<ButtonPress-3>', self._show_menu)

        # 双击
        self.canvas.bind('<Double-Button-1>', lambda e: self.next_anim())

        # 鼠标悬停说话
        self.canvas.bind('<Enter>', lambda e: self.random_speak())

        # 键盘快捷键
        self.root.bind('<Left>', lambda e: self.prev_anim())
        self.root.bind('<Right>', lambda e: self.next_anim())
        self.root.bind('<space>', lambda e: self.random_anim())
        self.root.bind('<w>', lambda e: self.toggle_walk())
        self.root.bind('<s>', lambda e: self.toggle_settings())
        self.root.bind('<c>', lambda e: self.show_chat())
        self.root.bind('<C>', lambda e: self.show_chat())
        # bind_all 确保无焦点时也能响应
        self._bind_chat_key()

    def _on_drag_start(self, e):
        self.is_dragging = True
        self.drag_x = e.x_root
        self.drag_y = e.y_root
        self._win_x = self.root.winfo_x()
        self._win_y = self.root.winfo_y()

    def _on_drag_move(self, e):
        if not self.is_dragging:
            return
        dx = e.x_root - self.drag_x
        dy = e.y_root - self.drag_y
        nx = self._win_x + dx
        ny = self._win_y + dy
        self.root.geometry(f"+{int(nx)}+{int(ny)}")

    def _on_drag_end(self, e):
        self.is_dragging = False

    def _show_menu(self, e):
        """显示右键菜单"""
        if self.menu_visible:
            self._hide_menu()
            return

        x = self.root.winfo_x() + e.x
        y = self.root.winfo_y() + e.y

        # 确保菜单不超出屏幕
        mw, mh = 180, 350
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = min(x, sw - mw)
        y = min(y, sh - mh)
        x = max(0, x)
        y = max(0, y)

        self.menu_win.geometry(f"+{int(x)}+{int(y)}")
        self.menu_win.deiconify()
        self.menu_win.lift()
        self.menu_visible = True

        # 点击其他地方关闭菜单
        self._menu_bind_id = self.root.bind('<Button-1>', self._on_click_outside_menu, add='+')

    def _on_click_outside_menu(self, e):
        """点击菜单外关闭菜单"""
        if not self.menu_visible:
            return
        mx = self.menu_win.winfo_x()
        my = self.menu_win.winfo_y()
        mw = self.menu_win.winfo_width()
        mh = self.menu_win.winfo_height()
        ex = e.x_root
        ey = e.y_root
        if not (mx <= ex <= mx + mw and my <= ey <= my + mh):
            self._hide_menu()

    def _hide_menu(self):
        self.menu_win.withdraw()
        self.menu_visible = False
        if hasattr(self, '_menu_bind_id'):
            try:
                self.root.unbind('<Button-1>', self._menu_bind_id)
            except:
                pass

    def _menu_action(self, cmd):
        """执行菜单命令"""
        self._hide_menu()
        cmd()

    # ─── 设置 ────────────────────────────────────

    def toggle_settings(self):
        """切换设置面板显示"""
        if self.settings_visible:
            self._close_settings()
        else:
            self._open_settings()

    def _open_settings(self):
        pw = self.root.winfo_x()
        py = self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        sw_w, sw_h = 340, 500
        x = pw + WINDOW_SIZE + 10
        y = py
        if x + sw_w > sw:
            x = max(0, pw - sw_w - 10)
        if y + sw_h > sh:
            y = max(0, sh - sw_h - 10)
        self.settings_win.geometry(f"+{int(x)}+{int(y)}")
        self.settings_win.deiconify()
        self.settings_win.lift()
        self.settings_visible = True

    def _close_settings(self):
        self.settings_win.withdraw()
        self.settings_visible = False

    def _on_resize(self, val):
        size = int(float(val))
        self.size_var.set(size)
        self.size_label.configure(text=str(size))
        if size != self.size:
            self._resize_window(size)
            self.config['size'] = size
            self.save_config()

    def _on_speed(self, val):
        self.speed = int(float(val))
        self.config['speed'] = self.speed
        self.save_config()

    def _on_auto_walk(self):
        self.auto_walk = self.walk_var.get()
        self.config['auto_walk'] = self.auto_walk
        self.save_config()

    def _on_interval(self, text):
        mapping = {"3秒": 3000, "5秒": 5000, "8秒": 8000, "15秒": 15000}
        ms = mapping.get(text, 5000)
        self.switch_interval = ms
        self.config['switch_interval'] = ms
        self.save_config()

    # ─── API 设置 ────────────────────────────────────

    def _toggle_key_show(self):
        self._key_hidden = not self._key_hidden
        self.api_key_entry.configure(show='*' if self._key_hidden else '')

    def _on_provider_change(self, e):
        p = self.api_provider_var.get()
        if p == 'openai':
            self.api_base_var.set('https://api.openai.com/v1')
            self.api_model_var.set('gpt-4o-mini')
        elif p == 'claude':
            self.api_base_var.set('https://api.anthropic.com')
            self.api_model_var.set('claude-sonnet-4-20250514')
        elif p == 'deepseek':
            self.api_base_var.set('https://api.deepseek.com')
            self.api_model_var.set('deepseek-chat')

    def _on_pick_color(self, name, hex_color):
        """色块点击选择气泡颜色"""
        self.bubble_color = hex_color
        self.bubble_color_var.set(name)
        self.config['bubble_color'] = hex_color
        self.save_config()
        # 刷新设置面板颜色预览
        if hasattr(self, 'color_preview'):
            self.color_preview.configure(bg=hex_color)

    def _on_proactive_toggle(self):
        self.proactive_chat = self.proactive_var.get()
        self.config['proactive_chat'] = self.proactive_chat
        self._save_proactive_config()
        if self.api_ready and self.proactive_chat:
            self._start_proactive_timer()
        else:
            self._stop_proactive_timer()

    def _on_proactive_rand_toggle(self):
        self.proactive_random = self.proactive_rand_var.get()
        self.config['proactive_random'] = self.proactive_random
        self._save_proactive_config()
        if self.proactive_chat and self.api_ready:
            self._start_proactive_timer()

    def _save_proactive_config(self):
        self.proactive_random = self.proactive_rand_var.get()
        self.proactive_interval = self.proactive_int_var.get()
        self.config['proactive_random'] = self.proactive_random
        self.config['proactive_interval'] = self.proactive_interval
        self.save_config()

    def _on_search_toggle(self):
        self.web_search = self.search_var.get()
        self.config['web_search'] = self.web_search
        self.save_config()

    def _save_api_settings(self):
        self.api_provider = self.api_provider_var.get()
        self.api_key = self.api_key_var.get()
        self.api_model = self.api_model_var.get()
        self.api_base = self.api_base_var.get().rstrip('/')
        self.api_system_prompt = self.api_sp_var.get()
        self.config.update({
            'api_provider': self.api_provider,
            'api_key': self.api_key,
            'api_model': self.api_model,
            'api_base': self.api_base,
            'api_system_prompt': self.api_system_prompt,
        })
        self.api_ready = bool(self.api_key and self.api_base)
        # 保存主动说话和搜索设置
        self.proactive_chat = self.proactive_var.get()
        self.proactive_random = self.proactive_rand_var.get()
        self.proactive_interval = self.proactive_int_var.get()
        self.web_search = self.search_var.get()
        self.config['proactive_chat'] = self.proactive_chat
        self.config['proactive_random'] = self.proactive_random
        self.config['proactive_interval'] = self.proactive_interval
        self.config['web_search'] = self.web_search
        if self.api_ready and self.proactive_chat:
            self._start_proactive_timer()
        else:
            self._stop_proactive_timer()
        # 同时保存快捷键
        new_key = self.chat_key_var.get().strip().lower() or 'c'
        if new_key != self.chat_key:
            self.chat_key = new_key
            self.config['chat_key'] = new_key
            self._bind_chat_key()
        self.save_config()
        self.chat_history = []
        if self.api_ready:
            self.api_status_label.configure(text="✅ 已保存", fg='#4CAF50')
        else:
            self.api_status_label.configure(text="⚠️ 请输入 API Key", fg='#FF9800')
        self.root.after(2000, lambda: self.api_status_label.configure(text=''))

    # ─── 对话窗口 ────────────────────────────────────

    def _bind_chat_key(self):
        """绑定快捷键（可配置）"""
        try:
            self.root.unbind_all(f'<KeyPress-{self._last_bound_key}>')
        except:
            pass
        key = self.chat_key.lower()
        self._last_bound_key = key
        self.root.bind_all(f'<KeyPress-{key}>', self._on_chat_key_global)

    def _on_chat_key_global(self, e):
        """全局快捷键：打开对话（排除正在输入的情况）"""
        if self.chat_visible:
            self._focus_chat()
            return
        widget = self.root.focus_get()
        if widget and isinstance(widget, (tk.Text, tk.Entry)):
            return
        self.show_chat()

    def show_chat(self):
        if self.chat_visible:
            self._focus_chat()
            return
        if not self.api_ready:
            self.say("请先在设置中配置 API Key 💬")
            return
        self._build_chat_window()
        self.chat_visible = True

    def _build_chat_window(self):
        self.chat_win = tk.Toplevel(self.root)
        self.chat_win.overrideredirect(True)
        self.chat_win.attributes('-topmost', True)
        self.chat_win.configure(bg=THEME['border'])
        cw, ch = 280, 135
        px = self.root.winfo_x() + WINDOW_SIZE + 10
        py = self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        if px + cw > sw:
            px = max(0, self.root.winfo_x() - cw - 10)
        self.chat_win.geometry(f"{cw}x{ch}+{px}+{py}")

        # 内层内容容器（边框效果）
        chat_inner = tk.Frame(self.chat_win, bg=THEME['bg'])
        chat_inner.pack(fill='both', expand=True, padx=1, pady=1)

        # 标题栏（accent 色底部边框）
        tb = tk.Frame(chat_inner, bg=THEME['surface'])
        tb.pack(fill='x')
        tk.Label(tb, text="💬  对我说...", fg=THEME['text_sec'], bg=THEME['surface'],
                 font=("Microsoft YaHei", 10), padx=12, pady=6).pack(side='left')
        cx_btn = tk.Label(tb, text="✕", fg=THEME['text_muted'], bg=THEME['surface'],
                          cursor="hand2",
                          font=("Microsoft YaHei", 13), padx=12, pady=6)
        cx_btn.pack(side='right')
        cx_btn.bind('<Enter>', lambda e: cx_btn.configure(fg=THEME['text']))
        cx_btn.bind('<Leave>', lambda e: cx_btn.configure(fg=THEME['text_muted']))
        cx_btn.bind('<Button-1>', lambda e: self._close_chat())
        # 标题栏底线
        tk.Frame(chat_inner, height=2, bg=THEME['accent']).pack(fill='x')

        # 输入区
        i_f = tk.Frame(chat_inner, bg=THEME['bg'])
        i_f.pack(fill='both', expand=True, padx=8, pady=(6, 2))
        # 带边框的输入框
        input_outer = tk.Frame(i_f, bg=THEME['border_light'], bd=1, relief='flat')
        input_outer.pack(fill='both', expand=True)
        self.chat_entry = tk.Text(input_outer, height=2, bg=THEME['input_bg'], fg=THEME['text'],
                                   font=("Microsoft YaHei", 11), bd=0,
                                   insertbackground=THEME['text'], wrap='word',
                                   padx=6, pady=4)
        self.chat_entry.pack(fill='both', expand=True)
        self.chat_entry.focus_set()

        # 按钮行
        b_f = tk.Frame(chat_inner, bg=THEME['bg'])
        b_f.pack(fill='x', padx=8, pady=(2, 8))
        self.thinking_label = tk.Label(b_f, text="", fg=THEME['text_muted'], bg=THEME['bg'],
                                       font=("Microsoft YaHei", 9))
        self.thinking_label.pack(side='left')
        self.send_btn = tk.Label(b_f, text="发送 (Enter)", fg=THEME['text'],
                                  bg=THEME['accent_dark'], cursor="hand2",
                                  font=("Microsoft YaHei", 10), padx=14, pady=4)
        self.send_btn.pack(side='right')
        self.send_btn.bind('<Enter>', lambda e: self.send_btn.configure(bg=THEME['accent']))
        self.send_btn.bind('<Leave>', lambda e: self.send_btn.configure(bg=THEME['accent_dark']))
        self.send_btn.bind('<Button-1>', lambda e: self._send_message())

        # 快捷键
        self.chat_entry.bind('<Return>', lambda e: self._on_chat_enter(e))
        self.chat_entry.bind('<Escape>', lambda e: self._close_chat())
        self._chat_focus_id = self.root.bind('<Button-1>',
            lambda e: self._on_click_outside_chat(e), add='+')

    def _on_chat_enter(self, e):
        if not (e.state & 0x0001):
            self._send_message()
            return 'break'

    def _focus_chat(self):
        if hasattr(self, 'chat_win') and self.chat_win.winfo_exists():
            self.chat_win.lift()
            self.chat_entry.focus_set()

    def _close_chat(self):
        self.chat_visible = False
        if hasattr(self, 'chat_win') and self.chat_win.winfo_exists():
            self.chat_win.destroy()
        if hasattr(self, '_chat_focus_id'):
            try:
                self.root.unbind('<Button-1>', self._chat_focus_id)
            except:
                pass

    def _on_click_outside_chat(self, e):
        if not hasattr(self, 'chat_win') or not self.chat_win.winfo_exists():
            return
        cx = self.chat_win.winfo_x()
        cy = self.chat_win.winfo_y()
        cw = self.chat_win.winfo_width()
        ch = self.chat_win.winfo_height()
        if not (cx <= e.x_root <= cx + cw and cy <= e.y_root <= cy + ch):
            self._close_chat()

    # ─── 统一 API 请求 ────────────────────────────

    def _api_request(self, messages, system_prompt='', max_tokens=300, temperature=0.8, timeout=30):
        """统一 API 请求，支持 OpenAI / Claude / 兼容接口"""
        if self.api_provider == 'claude':
            url = self.api_base.rstrip('/') + '/v1/messages'
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }
            payload = {
                "model": self.api_model,
                "system": system_prompt or '',
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            extract = lambda b: b['content'][0]['text']
        else:
            url = self.api_base.rstrip('/') + '/chat/completions'
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            full = [{"role": "system", "content": system_prompt}] if system_prompt else []
            full.extend(messages)
            payload = {
                "model": self.api_model,
                "messages": full,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            extract = lambda b: b['choices'][0]['message']['content']

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=timeout) as resp:
            body = json.loads(resp.read().decode('utf-8'))
        return extract(body).strip()

    def _time_context(self):
        """返回当前日期时间字符串"""
        import datetime
        now = datetime.datetime.now()
        tz = time.tzname[0] if time.daylight else time.tzname[0]
        return f"当前时间: {now.strftime('%Y-%m-%d %A %H:%M')} ({tz})"

    # ─── API 对话 ────────────────────────────────────

    def _send_message(self):
        if self._thinking:
            return
        text = self.chat_entry.get('1.0', 'end-1c').strip()
        if not text:
            return
        self.chat_entry.delete('1.0', 'end')
        self._thinking = True
        if hasattr(self, 'thinking_label') and self.thinking_label.winfo_exists():
            self.thinking_label.configure(text="🤔 思考中...")
        if hasattr(self, 'send_btn') and self.send_btn.winfo_exists():
            self.send_btn.configure(text="思考中...", bg='#555')
        self.say(text)
        if self.web_search:
            t = threading.Thread(target=self._call_api_with_search, args=(text,), daemon=True)
        else:
            t = threading.Thread(target=self._call_api, args=(text,), daemon=True)
        t.start()

    def _call_api(self, text):
        """带历史记录的手动对话"""
        try:
            system = self.api_system_prompt + '\n\n' + self._time_context()
            messages = [{"role": r, "content": c} for r, c in self.chat_history[-6:]]
            messages.append({"role": "user", "content": text})
            reply = self._api_request(messages, system, max_tokens=300, temperature=0.8)
            self.chat_history.append(("user", text))
            self.chat_history.append(("assistant", reply))
            self.root.after(0, lambda: self._handle_api_response(reply))
        except Exception as e:
            self.root.after(0, lambda: self._handle_api_error(str(e)))

    def _handle_api_response(self, reply):
        self._thinking = False
        if hasattr(self, 'thinking_label') and self.thinking_label.winfo_exists():
            self.thinking_label.configure(text="")
        if hasattr(self, 'send_btn') and self.send_btn.winfo_exists():
            self.send_btn.configure(text="发送 (Enter)", bg='#3a3a6a')
        self.say(reply)
        self.switch_gif(0)

    def _handle_api_error(self, error_msg):
        self._thinking = False
        if hasattr(self, 'thinking_label') and self.thinking_label.winfo_exists():
            self.thinking_label.configure(text="")
        if hasattr(self, 'send_btn') and self.send_btn.winfo_exists():
            self.send_btn.configure(text="发送 (Enter)", bg='#3a3a6a')
        short = error_msg[:40] + '...' if len(error_msg) > 40 else error_msg
        self.say(f"出错了: {short}")

    # --- Proactive chat ---

    def _proactive_prompt(self):
        """根据时段生成多样化的主动说话 prompt"""
        import datetime
        hour = datetime.datetime.now().hour

        prompts = [
            "请根据你的人格设定，说一句简短可爱的话（不超过30字）",
            "随意说点什么吧，符合你性格的（不超过30字）",
            "你现在心情怎么样？说句话吧（不超过30字）",
        ]

        # 时段特定语气
        if 6 <= hour < 9:
            prompts.append("早上了，用可爱的语气说句早安吧（不超过25字）")
        elif 9 <= hour < 12:
            prompts.append("上午好呀，随意聊点什么吧（不超过30字）")
        elif 12 <= hour < 14:
            prompts.append("中午了，说句跟午饭或休息有关的话（不超过25字）")
        elif 14 <= hour < 18:
            prompts.append("下午好，说句轻松的话吧（不超过30字）")
        elif 18 <= hour < 21:
            prompts.append("晚上了，说句傍晚问候吧（不超过25字）")
        elif 21 <= hour < 24:
            prompts.append("夜深了，说句温柔的话吧（不超过20字）")
        else:
            prompts.append("深夜了，轻轻说一句就好（不超过15字）")

        return random.choice(prompts)

    def _proactive_context(self):
        """构造最近聊天上下文（用于主动说话的连贯性）"""
        if not self.chat_history:
            return ''
        recent = self.chat_history[-4:]
        lines = []
        for role, content in recent:
            prefix = "你说" if role == 'assistant' else "对方说"
            lines.append(f"{prefix}: {content}")
        return '\n'.join(lines) + '\n'

    def _start_proactive_timer(self):
        if self._proactive_after:
            self.root.after_cancel(self._proactive_after)
        if self.proactive_chat and self.api_ready:
            self._schedule_next_proactive()

    def _stop_proactive_timer(self):
        if self._proactive_after:
            self.root.after_cancel(self._proactive_after)
            self._proactive_after = None

    def _do_proactive_chat(self):
        if not self.api_ready or not self.proactive_chat or self._thinking:
            self._schedule_next_proactive()
            return
        self._thinking = True
        self._proactive_timeout = self.root.after(20000, self._unstick_thinking)

        ctx = self._proactive_context()
        prompt = self._proactive_prompt()
        if ctx:
            prompt = f"最近对话:\n{ctx}\n请参考以上对话氛围，{prompt}"
        t = threading.Thread(target=self._call_proactive_api, args=(prompt,), daemon=True)
        t.start()

    def _call_proactive_api(self, text, retry=0):
        """主动说话（单轮，无历史）"""
        try:
            system = self.api_system_prompt + '\n\n' + self._time_context()
            reply = self._api_request(
                [{"role": "user", "content": text}],
                system, max_tokens=80, temperature=0.9, timeout=15,
            )
            self.root.after(0, lambda r=reply: self._handle_proactive_response(r, retry))
        except Exception:
            self._thinking = False
            if hasattr(self, '_proactive_timeout'):
                self.root.after_cancel(self._proactive_timeout)
            self._schedule_next_proactive()

    def _unstick_thinking(self):
        """超时复位 thinking 标志"""
        if self._thinking:
            self._thinking = False
            self._schedule_next_proactive()

    def _handle_proactive_response(self, reply, retry=0):
        self._thinking = False
        if hasattr(self, '_proactive_timeout'):
            self.root.after_cancel(self._proactive_timeout)
        if not reply or not reply.strip():
            if retry < 2:
                self._thinking = True
                prompt = self._proactive_prompt()
                t = threading.Thread(
                    target=self._call_proactive_api,
                    args=(prompt, retry + 1), daemon=True,
                )
                t.start()
                return
            # 重试完仍为空，跳过本次
            self._schedule_next_proactive()
            return
        self.say(reply)
        self.switch_gif(random.randint(0, len(GIF_NAMES) - 1))
        self.switch_gif(random.randint(0, len(GIF_NAMES) - 1))
        self._schedule_next_proactive()

    def _schedule_next_proactive(self):
        if self.proactive_chat and self.api_ready:
            if self.proactive_random:
                interval = random.randint(5, 120) * 1000
            else:
                interval = max(10, self.proactive_interval) * 1000
            self._proactive_after = self.root.after(interval, self._do_proactive_chat)

    # --- Web search ---

    def _search_web(self, query):
        try:
            q = urllib.parse.quote(query)
            url = f'https://api.duckduckgo.com/?q={q}&format=json&no_html=1'
            req = urllib.request.Request(url, headers={'User-Agent': 'RainbowPet/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode('utf-8'))
            parts = []
            if body.get('AbstractText'):
                parts.append(body['AbstractText'])
            for topic in body.get('RelatedTopics', []):
                if isinstance(topic, dict) and 'Text' in topic:
                    parts.append(topic['Text'])
                if len(parts) >= 5:
                    break
            return '\n'.join(parts) if parts else ''
        except:
            return ''

    def _call_api_with_search(self, text):
        """带联网搜索的手动对话"""
        search_context = self._search_web(text) if self.web_search else ''
        try:
            system = self.api_system_prompt + '\n\n' + self._time_context()
            if search_context:
                system += '\n\n当前网络信息（供参考）:\n' + search_context
            messages = [{"role": r, "content": c} for r, c in self.chat_history[-6:]]
            messages.append({"role": "user", "content": text})
            reply = self._api_request(messages, system, max_tokens=300, temperature=0.8)
            self.chat_history.append(("user", text))
            self.chat_history.append(("assistant", reply))
            self.root.after(0, lambda: self._handle_api_response(reply))
        except Exception as e:
            self.root.after(0, lambda: self._handle_api_error(str(e)))

    # ─── 配置持久化 ──────────────────────────────

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.config.update(data)
        except:
            pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

    # ─── 生命周期 ────────────────────────────────

    def run(self):
        """启动桌宠"""
        self.root.mainloop()

    def quit(self):
        """退出桌宠"""
        self._auto_switch_running = False
        self._walk_loop_running = False
        self._stop_proactive_timer()
        if self.anim_after:
            self.root.after_cancel(self.anim_after)
        if self.speech_after:
            self.root.after_cancel(self.speech_after)
        self.save_config()
        self.running = False
        self.root.destroy()
        sys.exit(0)


# ─── 启动 ─────────────────────────────────────────

if __name__ == '__main__':
    # 切换到程序目录
    os.chdir(BASE_DIR)
    pet = DesktopPet()
    pet.run()
