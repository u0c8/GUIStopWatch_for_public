import flet as ft
import time
import threading
from playsound import playsound
from sound_list import path_sounds

class stop_watch:
    start_time = 0
    stop_time = None
    sflags = None
    
    def __init__(self):
        self.sound_flags_reset()

    def sound_flags_reset(self):
        self.sflags = {
            "30sec" : True,
            "1min" : False,
            "2min" : False,
            "3min" : False,
            "4min" : False,
            "5min" : True,
            "6min" : False,
            "7min" : False,
            "8min" : True,
            "9min" : False,
            "10min" : True,
            "11min" : False,
            "12min" : True,
            "13min" : False,
            "14min" : False,
            "15min" : True,
        }

    def play(self, time):
        time = int(time)
        t = threading.Timer(0.1, lambda : self.play(self.current_time()))
        if self.sflags["30sec"] and time == 30 :
            playsound(path_sounds["30sec"])
            self.sflags["30sec"] = False
            t.start()
            return
        
        min = int(time // 60)
        if min == 0:
            t.start()
            return
        key = str(min) + "min"
        if self.sflags[key] :
            print(key)
            playsound(path_sounds[key])
            self.sflags[key] = False
            t.start()
            return

    # Noneのときは開始できる
    def is_start(self):
        return self.start_time == 0

    def start(self):
        self.start_time = time.time()

    # 初期状態に戻す
    def reset(self):
        self.start_time = 0
        self.stop_time = None

    def is_stop(self):
        return self.stop_time != None

    def stop(self):
        self.stop_time = time.time()

    def restart(self):
        current_time = time.time()
        stop_while_time = current_time - self.stop_time
        self.start_time += stop_while_time
        self.stop_time = None

    def current_time(self):
        if self.start_time == 0:
            current_time = 0
        elif self.stop_time == None:
            current_time = time.time()
        else:
            current_time = self.stop_time
        
        return current_time - self.start_time
    
    def convert(sec):
        minits = sec // 60
        second = sec % 60
        milli_sec = (second - int(second)) * 1000
        hour = minits // 60
        min = minits % 60
        return f"{int(hour):02d}:{int(min):02d}:{int(second):02d}:{int(milli_sec // 10):02d}"

def main(page: ft.Page):
    def worker():
        text_time.value = stop_watch.convert(sw.current_time())
        page.update()
        time.sleep(8)

    def scheduler(interval, f, wait = True):
        base_time = time.time()
        next_time = 0
        while True:
            t = threading.Thread(target = f)
            t.start()
            if wait:
                t.join()
            next_time = ((base_time - time.time()) % interval) or interval
            time.sleep(next_time)

    def btn_start(e):
        if sw.is_start():
            sw.start()

    def btn_reset(e):
        sw.reset()

    def btn_stop(e):
        if sw.is_stop():
            sw.restart()
        else :
            sw.stop()

    sw = stop_watch()
    page.title = "ゆかりんウォッチ　べーた！"
    page.window_width = 1400
    page.window_height = 1000
    page.window_resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    text_time = ft.Text(value="Test", size=200)
    # 目パチ用画像
    yukari_wink_image_path = [
        # 通常
        "./psd/shiratsu_yukari_1.png",
        # 半目
        "./psd/shiratsu_yukari_1.1.png",
        # 閉じ
        "./psd/shiratsu_yukari_1.2.png",
    ]
    yukari_image = ft.Image(
        src=None,
        fit=ft.ImageFit.CONTAIN,
        opacity=0.8,
    )
    
    class Wink:

        def __init__(self):
            pass

        def update(self,index):
            yukari_image.src = yukari_wink_image_path[index]

        def open(self):
            self.update(0)
            t = threading.Timer(7, lambda : self.half_close())
            t.start()

        def half_close(self):
            self.update(1)
            t = threading.Timer(0.1, lambda : self.close())
            t.start()

        def half_open(self):
            self.update(1)
            t = threading.Timer(0.1, lambda : self.open())
            t.start()

        def close(self):
            self.update(2)
            t = threading.Timer(0.1, lambda : self.half_open())
            t.start()
        
    wink = Wink()

    body = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        text_time,
                    ],
                    # alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(text="開始", on_click=lambda e:btn_start(e)),
                        ft.ElevatedButton(text="停止/再開", on_click=lambda e:btn_stop(e)),
                        ft.ElevatedButton(text="リセット", on_click=lambda e:btn_reset(e)),
                    ],
                    # alignment=ft.MainAxisAlignment.CENTER
                ),
            ],
            # alignment=ft.MainAxisAlignment.CENTER
        ),
        alignment=ft.alignment.Alignment(0.5, 0.5),
        margin=ft.margin.only(left=30),
    )

    yukari_container = ft.Container(
        content=yukari_image,
        # width=400,
        height=1000,
        margin=0,
        padding=ft.padding.only(top=300, left=0),
        alignment=ft.alignment.bottom_center
    )

    page.padding = 0
    page.add(
        ft.Row(
        [
            body,
            yukari_container,
        ],
        alignment=ft.MainAxisAlignment.CENTER
        )
    )
    
    wink.open()
    sw.play(sw.current_time())
    scheduler(0.01, worker, False)

ft.app(target=main)