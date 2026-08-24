import random
import copy

import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.metrics import dp

# ============================================================
# مهم جداً: خط يدعم العربي
# حمّل خط عربي مجاني (مثل NotoNaskhArabic-Regular.ttf أو Amiri-Regular.ttf)
# وضعه بنفس مجلد main.py باسم: arabic_font.ttf
# بدون هذا الخط، الحروف العربية ما راح تظهر أبداً (مربعات فارغة)
# ============================================================
try:
    LabelBase.register(name="Arabic", fn_regular="arabic_font.ttf")
    ARABIC_FONT = "Arabic"
except Exception:
    ARABIC_FONT = None  # لو الخط مو موجود، يشتغل بالخط الافتراضي (بدون دعم عربي صحيح)


def ar(text):
    """إصلاح اتجاه وشكل النص العربي للعرض"""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# ---------- بيانات اللاعب (تُحفظ داخل الـ App) ----------
def new_player():
    return {
        "name": "بطل",
        "level": 1,
        "hp": 100,
        "max_hp": 100,
        "attack": 10,
        "defense": 5,
        "exp": 0,
        "exp_to_next": 30,
        "gold": 0,
        "weapon": "سيف خشبي",
        "armor": "درع جلدي",
        "potions": 3,
    }


BASE_ENEMIES = [
    {"name": "زومبي", "hp": 30, "attack": 8, "defense": 2, "exp": 15, "gold": 10},
    {"name": "ذئب متوحش", "hp": 40, "attack": 12, "defense": 3, "exp": 20, "gold": 15},
    {"name": "ساحر مظلم", "hp": 50, "attack": 15, "defense": 5, "exp": 25, "gold": 20},
    {"name": "شيطان الجحيم", "hp": 70, "attack": 20, "defense": 8, "exp": 35, "gold": 30},
]


def generate_enemy(player):
    max_index = min(player["level"] // 2, len(BASE_ENEMIES) - 1)
    enemy = copy.deepcopy(random.choice(BASE_ENEMIES[: max_index + 1]))
    boost = 1 + (player["level"] - 1) * 0.15
    for k in ("hp", "attack", "defense", "exp", "gold"):
        enemy[k] = int(enemy[k] * boost)
    enemy["max_hp"] = enemy["hp"]
    return enemy


def make_label(text, size_hint_y=None, height=dp(30), font_size=18):
    lbl = Label(
        text=ar(text),
        font_name=ARABIC_FONT,
        size_hint_y=size_hint_y,
        height=height,
        font_size=font_size,
        halign="right",
        valign="middle",
    )
    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
    return lbl


def make_button(text, callback, height=dp(55), font_size=20):
    btn = Button(
        text=ar(text),
        font_name=ARABIC_FONT,
        size_hint_y=None,
        height=height,
        font_size=font_size,
    )
    btn.bind(on_release=callback)
    return btn


# ---------- شاشة القائمة الرئيسية ----------
class MenuScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        app = App.get_running_app()
        p = app.player

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        root.add_widget(make_label("⚔️ صياد الظل ⚔️", height=dp(45), font_size=26))
        root.add_widget(
            make_label(f"❤️ HP: {p['hp']}/{p['max_hp']}  |  📈 المستوى: {p['level']}")
        )
        root.add_widget(
            make_label(f"💰 الذهب: {p['gold']}  |  🧪 الجرعات: {p['potions']}")
        )

        root.add_widget(make_button("⚔️ استكشاف (قتال عدو)", self.go_combat))
        root.add_widget(make_button("🏪 المتجر", self.go_shop))
        root.add_widget(make_button("📊 حالة البطل", self.go_status))

        root.add_widget(BoxLayout())  # مسافة فارغة
        self.add_widget(root)

    def go_combat(self, *_):
        self.manager.current = "combat"

    def go_shop(self, *_):
        self.manager.current = "shop"

    def go_status(self, *_):
        self.manager.current = "status"


# ---------- شاشة القتال ----------
class CombatScreen(Screen):
    enemy = None

    def on_pre_enter(self):
        app = App.get_running_app()
        self.enemy = generate_enemy(app.player)
        self.log = [f"⚔️ واجهت {self.enemy['name']}!"]
        self.build()

    def build(self):
        self.clear_widgets()
        app = App.get_running_app()
        p = app.player

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))

        self.status_label = make_label(
            f"❤️ أنت: {p['hp']}/{p['max_hp']}   💀 {self.enemy['name']}: {self.enemy['hp']}/{self.enemy['max_hp']}",
            height=dp(40),
        )
        root.add_widget(self.status_label)

        scroll = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text=ar("\n".join(self.log)),
            font_name=ARABIC_FONT,
            size_hint_y=None,
            halign="right",
            valign="top",
            font_size=16,
        )
        self.log_label.bind(
            texture_size=lambda *_: setattr(self.log_label, "height", self.log_label.texture_size[1])
        )
        self.log_label.bind(width=lambda *_: setattr(self.log_label, "text_size", (self.log_label.width, None)))
        scroll.add_widget(self.log_label)
        root.add_widget(scroll)

        btn_row1 = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_row1.add_widget(make_button("⚔️ هجوم", self.attack))
        btn_row1.add_widget(make_button("🛡️ دفاع", self.defend))
        root.add_widget(btn_row1)

        btn_row2 = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_row2.add_widget(make_button("🧪 جرعة", self.use_potion))
        btn_row2.add_widget(make_button("🏃 هروب", self.flee))
        root.add_widget(btn_row2)

        self.add_widget(root)

    def add_log(self, text):
        self.log.append(text)
        self.log = self.log[-8:]  # آخر 8 أسطر بس
        self.log_label.text = ar("\n".join(self.log))

    def refresh_status(self):
        app = App.get_running_app()
        p = app.player
        self.status_label.text = ar(
            f"❤️ أنت: {p['hp']}/{p['max_hp']}   💀 {self.enemy['name']}: {max(0, self.enemy['hp'])}/{self.enemy['max_hp']}"
        )

    def enemy_turn(self):
        app = App.get_running_app()
        p = app.player
        dmg = max(1, self.enemy["attack"] - p["defense"] // 2 + random.randint(-2, 3))
        p["hp"] -= dmg
        self.add_log(f"💢 {self.enemy['name']} ضربك بـ {dmg} ضرر!")

    def check_end(self):
        app = App.get_running_app()
        p = app.player
        if self.enemy["hp"] <= 0:
            self.add_log(f"🎉 قتلت {self.enemy['name']}!")
            p["exp"] += self.enemy["exp"]
            p["gold"] += self.enemy["gold"]
            self.add_log(f"⭐ +{self.enemy['exp']} خبرة | 💰 +{self.enemy['gold']} ذهب")
            leveled = self.level_up(p)
            if leveled:
                self.add_log(f"🎉 مستوى جديد! أنت الآن {p['level']}")
            return True
        if p["hp"] <= 0:
            self.add_log(f"💀 قُتلت على يد {self.enemy['name']}!")
            self.manager.current = "gameover"
            return True
        return False

    def level_up(self, p):
        leveled = False
        while p["exp"] >= p["exp_to_next"]:
            p["exp"] -= p["exp_to_next"]
            p["level"] += 1
            p["max_hp"] += 20
            p["hp"] = p["max_hp"]
            p["attack"] += 5
            p["defense"] += 3
            p["exp_to_next"] = int(p["exp_to_next"] * 1.5)
            leveled = True
        return leveled

    def attack(self, *_):
        app = App.get_running_app()
        p = app.player
        dmg = max(1, p["attack"] - self.enemy["defense"] // 2 + random.randint(-3, 5))
        self.enemy["hp"] -= dmg
        self.add_log(f"💥 ضربت {self.enemy['name']} بـ {dmg} ضرر!")
        if self.check_end():
            self.refresh_status()
            return
        self.enemy_turn()
        self.refresh_status()
        self.check_end()

    def defend(self, *_):
        app = App.get_running_app()
        p = app.player
        p["defense"] += 5
        self.add_log("🛡️ رفعت درعك!")
        dmg = max(1, self.enemy["attack"] - p["defense"] // 2 + random.randint(-2, 3))
        p["hp"] -= dmg
        p["defense"] -= 5
        self.add_log(f"💢 {self.enemy['name']} ضربك بـ {dmg} ضرر!")
        self.refresh_status()
        self.check_end()

    def use_potion(self, *_):
        app = App.get_running_app()
        p = app.player
        if p["potions"] > 0:
            p["hp"] = min(p["max_hp"], p["hp"] + 30)
            p["potions"] -= 1
            self.add_log("🧪 استخدمت جرعة! +30 HP")
        else:
            self.add_log("❌ ليس لديك جرعات!")
        self.refresh_status()

    def flee(self, *_):
        if random.random() < 0.5:
            self.add_log("🏃 هربت بنجاح!")
            self.manager.current = "menu"
        else:
            self.add_log("❌ فشل الهروب!")
            self.enemy_turn()
            self.refresh_status()
            self.check_end()


# ---------- شاشة المتجر ----------
class ShopScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        app = App.get_running_app()
        p = app.player

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        root.add_widget(make_label("🏪 المتجر", height=dp(40), font_size=24))
        self.gold_label = make_label(f"💰 لديك: {p['gold']} ذهب")
        root.add_widget(self.gold_label)

        scroll = ScrollView()
        items = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        items.bind(minimum_height=items.setter("height"))

        items.add_widget(make_button("🗡️ سيف حديدي (+5 هجوم) - 30 ذهب", lambda *_: self.buy("weapon", "سيف حديدي", "attack", 5, 30)))
        items.add_widget(make_button("🛡️ درع فولاذي (+5 دفاع) - 30 ذهب", lambda *_: self.buy("armor", "درع فولاذي", "defense", 5, 30)))
        items.add_widget(make_button("🧪 جرعة (+30 HP) - 15 ذهب", lambda *_: self.buy_potion()))
        items.add_widget(make_button("⚔️ سيف الظل (+12 هجوم) - 80 ذهب", lambda *_: self.buy("weapon", "سيف الظل", "attack", 12, 80)))
        items.add_widget(make_button("🛡️ درع الأسطورة (+12 دفاع) - 80 ذهب", lambda *_: self.buy("armor", "درع الأسطورة", "defense", 12, 80)))

        scroll.add_widget(items)
        root.add_widget(scroll)

        self.msg_label = make_label("", height=dp(30))
        root.add_widget(self.msg_label)

        root.add_widget(make_button("⬅️ رجوع", self.back))
        self.add_widget(root)

    def buy(self, slot, name, stat, amount, cost):
        app = App.get_running_app()
        p = app.player
        if p["gold"] >= cost:
            p["gold"] -= cost
            p[slot] = name
            p[stat] += amount
            self.msg_label.text = ar(f"✅ اشتريت {name}!")
        else:
            self.msg_label.text = ar("❌ ذهب غير كافٍ!")
        self.gold_label.text = ar(f"💰 لديك: {p['gold']} ذهب")

    def buy_potion(self):
        app = App.get_running_app()
        p = app.player
        if p["gold"] >= 15:
            p["gold"] -= 15
            p["potions"] += 1
            self.msg_label.text = ar("✅ اشتريت جرعة!")
        else:
            self.msg_label.text = ar("❌ ذهب غير كافٍ!")
        self.gold_label.text = ar(f"💰 لديك: {p['gold']} ذهب")

    def back(self, *_):
        self.manager.current = "menu"


# ---------- شاشة حالة البطل ----------
class StatusScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        app = App.get_running_app()
        p = app.player

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        root.add_widget(make_label("📊 حالة البطل", height=dp(40), font_size=24))
        root.add_widget(make_label(f"📛 الاسم: {p['name']}"))
        root.add_widget(make_label(f"📈 المستوى: {p['level']}"))
        root.add_widget(make_label(f"❤️ HP: {p['hp']}/{p['max_hp']}"))
        root.add_widget(make_label(f"⚔️ الهجوم: {p['attack']}"))
        root.add_widget(make_label(f"🛡️ الدفاع: {p['defense']}"))
        root.add_widget(make_label(f"⭐ الخبرة: {p['exp']}/{p['exp_to_next']}"))
        root.add_widget(make_label(f"💰 الذهب: {p['gold']}"))
        root.add_widget(make_label(f"🗡️ السلاح: {p['weapon']}"))
        root.add_widget(make_label(f"🛡️ الدرع: {p['armor']}"))
        root.add_widget(make_label(f"🧪 الجرعات: {p['potions']}"))
        root.add_widget(BoxLayout())
        root.add_widget(make_button("⬅️ رجوع", lambda *_: setattr(self.manager, "current", "menu")))
        self.add_widget(root)


# ---------- شاشة نهاية اللعبة ----------
class GameOverScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        app = App.get_running_app()
        p = app.player

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        root.add_widget(make_label("☠️ انتهت اللعبة ☠️", height=dp(45), font_size=26))
        root.add_widget(make_label(f"📈 المستوى: {p['level']}"))
        root.add_widget(make_label(f"⭐ الخبرة: {p['exp']}"))
        root.add_widget(make_label(f"💰 الذهب: {p['gold']}"))
        root.add_widget(BoxLayout())
        root.add_widget(make_button("🔄 إعادة اللعب", self.restart))
        self.add_widget(root)

    def restart(self, *_):
        app = App.get_running_app()
        app.player = new_player()
        self.manager.current = "menu"


class ShadowHunterApp(App):
    def build(self):
        self.player = new_player()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CombatScreen(name="combat"))
        sm.add_widget(ShopScreen(name="shop"))
        sm.add_widget(StatusScreen(name="status"))
        sm.add_widget(GameOverScreen(name="gameover"))
        return sm


if __name__ == "__main__":
    ShadowHunterApp().run()
