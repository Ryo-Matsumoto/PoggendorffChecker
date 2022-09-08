import sdl2 
import sdl2.ext
import sdl2.sdlttf

import tkinter as tk
import tkinter.font as font
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

import ctypes
import math 

class PoggendorffChecker(tk.Frame):
    SHOW_CORRECT_MESSAGE = 'show the correct line'.encode('utf-8')

    def __init__(self, master:tk.Tk, font_path: str):
        super().__init__(master)
        master.title('PoggendorffChecker')
        
        self.window = None
        self.renderer = None
        self.world = None

        # 1ピクセル当たりの長さ[cm]
        self.cm_per_pixel = 1/master.winfo_fpixels('1c')

        # 遮蔽四角形における座標・サイズ
        self.rec_x, self.rec_y, self.rec_w, self.rec_h = 220, 50, 60, 400
        self.cx, self.cy =  self.rec_x+self.rec_w//2, self.rec_y+self.rec_h//2
        
        # 直線PQの長さ
        self.line_length = 500

        # 直線PMにおける座標
        self.pm_x, self.pm_y = None, None

        # 直線NQにおける座標
        self.nq_x, self.nq_y = None, None
        # 直線NQの動きの方向と速度と範囲
        self.move = -1
        self.dy = 0.1
        self.min_nq_y, self.max_nq_y = None, None
        # 真の直線NQにおける座標
        self.correct_nq_x, self.correct_nq_y = None, None

        # pysdl2埋め込み用フレーム
        master.update_idletasks()
        self.embed = tk.Frame(master, width = 500, height = 500)
        self.embed.grid(row=0, column=0, rowspan=30)

        # コンソール
        label_console = tk.Label(master, text="console")
        label_console.grid(row=0, column=1, columnspan = 2, sticky=(tk.S))
        f = font.Font(family='Helvetica', size=10)
        self.console = tk.Text(master,width=30)
        self.console.configure(font=f)
        self.console.insert(1.0, "θ[°], d[cm]\n")
        self.console.configure(state='disabled')
        self.console.grid(row=1, column=1, rowspan=26, sticky=(tk.N, tk.W, tk.S, tk.E))

        # スクロールバー
        scrollbar = tk.Scrollbar(
            orient='vertical',
            command=self.console.yview)
        self.console['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=1, column=2, rowspan=26, sticky=(tk.N,tk.S))

        # コンソールの内容をcsv形式で保存
        self.buttons = tk.Frame(master)
        self.button = tk.Button(self.buttons, text = "save as csv", command=self.save_console, width = 15)
        self.buttons.grid(row=28, column=1, columnspan = 2,sticky=(tk.N, tk.W))
        self.button.pack(side="left", padx=0)

        # コンソールの内容をクリア
        self.buttons = tk.Frame(master)
        self.button = tk.Button(self.buttons, text = "clear", command=self.clear_console, width = 15)
        self.buttons.grid(row=28, column=1, columnspan = 2, sticky=(tk.N, tk.E))
        self.button.pack(side="left", padx=0)

        # 傾き調整
        self.theta = 90
        self.grad = tk.Frame(master)
        self.scale_var_theta = tk.IntVar(value=self.theta)
        label_sub_theta = tk.Label(self.grad, text="θ")
        self.scale_theta = tk.Scale(self.grad, variable = self.scale_var_theta, orient=tk.HORIZONTAL, length = 600,  width = 20,  sliderlength = 20,  from_ = 10, to = 90, resolution=10, command=self.set_theta)
        self.grad.grid(row=30, column=0, columnspan = 3)
        label_sub_theta.pack(side="left", padx=0)
        self.scale_theta.pack(side="left", padx=4)

        # 再生と停止
        self.play = False
        self.buttons = tk.Frame(master)
        self.button = tk.Button(self.buttons, text = "start/stop", width = 60, command=self.set_play, repeatdelay=500, repeatinterval=25)
        self.buttons.grid(row=31, column=0, columnspan = 3)
        self.button.pack(side="left", padx=0)

        # 真の直線PQの表示有無
        self.show_correct = False
        self.font_path = font_path.encode('utf-8')
        self.font = None
        self.surface = None
        self.message = None
        self.message_x, self.message_y = 40, 20
        self.message_w, self.message_h = None, None
        self.checkbox_dx = 15

        # ×ボタンクリック
        master.protocol("WM_DELETE_WINDOW", self.stop_run)
        master.update()

        # キーボード
        master.bind("<KeyPress>",self.key_handler)

        # マウス
        self.mouse_x, self.mouse_y = None, None
        self.mouse_button_down = False
        
        # メインループ
        self.running = True
        
    # 各種初期化
    def init(self):
        sdl2.ext.init()
        self.init_window()
        self.init_renderer()
        self.init_world()
        self.init_correct_line()
        sdl2.SDL_RenderPresent(self.renderer)
        
        self.set_PM()
        self.init_NQ()

        self.draw()

    def init_window(self):
        self.window =  sdl2.SDL_CreateWindowFrom(self.embed.winfo_id())

    def init_renderer(self):
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, 0)

    def init_world(self):
        self.world = sdl2.ext.World()

    def init_correct_line(self):
        sdl2.sdlttf.TTF_Init()
        self.font = sdl2.sdlttf.TTF_OpenFont(self.font_path, 12)
        self.surface = sdl2.sdlttf.TTF_RenderText_Solid(self.font, self.SHOW_CORRECT_MESSAGE, sdl2.SDL_Color(0, 0, 0))

        self.message = sdl2.SDL_CreateTextureFromSurface(self.renderer, self.surface)
        self.message_w, self.message_h = self.surface.contents.w, self.surface.contents.h
        sdl2.SDL_FreeSurface(self.surface)

    def init_NQ(self):
        self.correct_nq_x = self.cx + int(self.line_length//2 * math.sin(math.radians(self.theta)))
        self.correct_nq_y = self.cy - int(self.line_length//2 * math.cos(math.radians(self.theta)))
        self.min_nq_y = self.rec_y + int((self.rec_w/2)/ math.tan(math.radians(self.theta)))
        self.max_nq_y = self.rec_y + self.rec_h - int(self.line_length//2 * math.cos(math.radians(self.theta))) - 1
        self.nq_x = self.cx + int(self.line_length//2 * math.sin(math.radians(self.theta)))
        self.nq_y = self.max_nq_y

    # コンソールの内容をcsv形式で保存
    def save_console(self):
        filename = filedialog.asksaveasfilename(filetypes = [("CSV", ".csv")],defaultextension = "csv")
        if not filename == '':
            try:
                with open(filename, mode='w') as f:
                    f.write(self.console.get("1.0", "end"))
            except PermissionError:
                messagebox.showwarning(title='PoggendorffChecker', message='This file is in use. Please enter a new name or close the file opened in another program.')
    
    # コンソールの内容をクリア
    def clear_console(self):
        self.console.configure(state='normal')
        self.console.delete("1.0","end")
        self.console.insert(1.0, "θ[°], d[cm]\n")
        self.console.configure(state='disabled')

    # 傾きθを設定
    def set_theta(self, val):
        self.theta = self.scale_var_theta.get()

    # 再生/停止を設定
    def set_play(self):
        self.play = not self.play
        if not self.play:
            self.console.configure(state='normal')
            d = ((self.nq_y - self.line_length//2 * math.cos(math.radians(self.theta))) - self.correct_nq_y)*self.cm_per_pixel + 0.005
            self.console.insert(tk.END,"{}, {:.02f}\n".format(self.theta, d))
            self.console.configure(state='disabled')

    # NQを更新
    def set_NQ(self):
        self.correct_nq_x = self.cx + int(self.line_length//2 * math.sin(math.radians(self.theta)))
        self.correct_nq_y = self.cy - int(self.line_length//2 * math.cos(math.radians(self.theta)))
        self.min_nq_y = self.rec_y + int((self.rec_w/2)/ math.tan(math.radians(self.theta)))
        self.nq_x = self.cx + int(self.line_length//2 * math.sin(math.radians(self.theta)))
        
        if self.nq_y <= self.min_nq_y:
            if self.nq_y < self.min_nq_y:
                self.nq_y = self.min_nq_y
            self.move = 1
        if self.nq_y >= self.max_nq_y:
            if self.nq_y > self.max_nq_y:
                self.nq_y = self.max_nq_y
            self.move = -1

        self.nq_y += self.play * self.move * self.dy * (self.max_nq_y - self.min_nq_y)/(self.rec_h/2)
    
    # PMを更新
    def set_PM(self):
        self.pm_x = self.cx - int(self.line_length//2 * math.sin(math.radians(self.theta)))
        self.pm_y = self.cy + int(self.line_length//2 * math.cos(math.radians(self.theta)))

    # 真の直線PQを描画するかを設定
    def set_correct_line(self):
        self.show_correct = not self.show_correct

    # プログラムを終了
    def stop_run(self):
        self.running = False

    # アニメーションのフラッシュ
    def flush_renderer(self):
        sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255, 255, 255)
        sdl2.SDL_RenderClear(self.renderer)

    # 1フレームを描画
    def draw(self):
        self.flush_renderer()

        # 直線PM
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, ctypes.c_ubyte(255))
        self.set_PM()
        sdl2.SDL_RenderDrawLine(self.renderer, self.pm_x, self.pm_y, self.cx, self.cy)

        # 直線NQ
        self.set_NQ()
        sdl2.SDL_RenderDrawLine(self.renderer, self.cx, int(self.nq_y), self.nq_x, int(self.nq_y - self.line_length//2 * math.cos(math.radians(self.theta))))

        # 遮蔽四角形
        sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255, 255, ctypes.c_ubyte(255))
        sdl2.SDL_RenderFillRect(self.renderer, sdl2.SDL_Rect(self.rec_x, self.rec_y, self.rec_w, self.rec_h))
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, ctypes.c_ubyte(255))
        sdl2.SDL_RenderDrawRect(self.renderer, sdl2.SDL_Rect(self.rec_x, self.rec_y, self.rec_w, self.rec_h))

        # 真の直線PQ
        sdl2.SDL_RenderCopy(self.renderer, self.message, None, sdl2.SDL_Rect(self.message_x, self.message_y, self.message_w, self.message_h)) 
        sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255*(not self.show_correct), 255*(not self.show_correct), ctypes.c_ubyte(255))
        sdl2.SDL_RenderFillRect(self.renderer, sdl2.SDL_Rect(self.message_x-self.checkbox_dx, self.message_y, self.message_h, self.message_h))
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, ctypes.c_ubyte(255))
        sdl2.SDL_RenderDrawRect(self.renderer, sdl2.SDL_Rect(self.message_x-self.checkbox_dx, self.message_y, self.message_h, self.message_h))
        if self.show_correct:
            sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 0, 0, ctypes.c_ubyte(255))
            sdl2.SDL_RenderDrawLine(self.renderer,self.pm_x, self.pm_y, self.correct_nq_x, self.correct_nq_y)

        # レンダリング
        sdl2.SDL_RenderPresent(self.renderer)

    # キーボード制御
    def key_handler(self, event):
        if event.keysym=="Escape":
            self.stop_run()
        elif event.keysym == "space":
            self.set_play()

    # マウス制御
    def mouse_handler(self, events):
        for event in events:
            if event.type == sdl2.SDL_MOUSEMOTION:
                motion = event.motion
                self.mouse_x, self.mouse_y = motion.x, motion.y

            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                if sorted([self.message_x-self.checkbox_dx, self.mouse_x, self.message_x-self.checkbox_dx+self.message_h])[1] == self.mouse_x\
                    and sorted([self.message_y, self.mouse_y, self.message_y+self.message_h])[1] == self.mouse_y:
                    self.mouse_button_down = True
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                if sorted([self.message_x-self.checkbox_dx, self.mouse_x, self.message_x-self.checkbox_dx+self.message_h])[1] == self.mouse_x\
                    and sorted([self.message_y, self.mouse_y, self.message_y+self.message_h])[1] == self.mouse_y and self.mouse_button_down:
                    self.set_correct_line()
                    self.mouse_button_down = False

    # メインループを回す
    def run(self):
        self.init()
        self.flush_renderer()

        # メインループ本体
        while self.running:
            self.draw()

            events = sdl2.ext.get_events()
            if events is not None:
                self.mouse_handler(events)

            self.world.process()
            self.master.update()

            sdl2.SDL_Delay(10)
        
        sdl2.SDL_DestroyTexture(self.message)

