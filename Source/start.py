import os
import sys
import platform
import threading
import time

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

try:
    from prompt_toolkit import Application
    from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl, FloatContainer, Float, DynamicContainer, ConditionalContainer
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.widgets import Frame, TextArea, Label, Button, Shadow, RadioList
    from prompt_toolkit.patch_stdout import patch_stdout
except ImportError:
    print("Error: Missing libraries. Run: pip install rich prompt_toolkit requests python-a2s")
    sys.exit(1)

from data_manager import DataManager
from live_updates import LiveUpdater
from mod_manager import ModManager
from server_actions import ServerActions
from views import ViewRenderer
from keybindings import KeyBinder
from constants import VERSION, APP_NAME, DEFAULT_PROFILE_NAME

if platform.system() == "Windows":
    try:
        from windows.utils import get_steam_path, get_dayz_path
    except ImportError:
        def get_steam_path(): return None
        def get_dayz_path(p): return None
else:
    try:
        from linux.utils import get_steam_path, get_dayz_path
    except ImportError:
        def get_steam_path(): return None
        def get_dayz_path(p): return None

class DayZLauncherTUI:
    def __init__(self):
        self.data_manager = DataManager()
        self.mod_manager = ModManager(self.data_manager.config)
        self.server_actions = ServerActions(self.data_manager.config)
        self.view_renderer = ViewRenderer(self.data_manager.config)
        
        current_path = self.data_manager.config.get("dayz_path")
        sys_type = platform.system()
        is_linux = sys_type == "Linux"
        
        # Validate path
        path_invalid = False
        if current_path and current_path != "CANNOT FIND PATH":
            if is_linux and ("\\" in current_path or ":" in current_path):
                path_invalid = True
            elif sys_type == "Windows" and current_path.startswith("/"):
                path_invalid = True
        
        if not current_path or path_invalid or current_path == "CANNOT FIND PATH":
            steam = get_steam_path()
            path = get_dayz_path(steam)
            if path:
                self.data_manager.config.set("dayz_path", path)
            else:
                if not current_path: # set only if empty
                     self.data_manager.config.set("dayz_path", "CANNOT FIND PATH")

        self.selected_index = 0
        self.refresh_lock = threading.Lock()
        self.search_timer = None
        self.current_tab = "GLOBAL" 
        self.tabs = ["GLOBAL", "FAVORITES", "RECENT", "SETTINGS", "MODS"]
        self.show_launch_dialog = False
        self.launch_message = ""
        
        self.live_updater = LiveUpdater(
             self.data_manager.browser, 
             self.data_manager.live_info,
             lambda: self.app.invalidate() if hasattr(self, 'app') else None
        )

        self._init_widgets()
        
        self.key_binder = KeyBinder(self)
        self.kb = self.key_binder.get_global_bindings()
        self.content_control.key_bindings = self.key_binder.get_list_bindings()
        
        self._init_layout()

        self.live_updater.start_loop(
            lambda: self.data_manager.filtered_servers,
            lambda: self.selected_index
        )
        
        self.refresh_data()
        self._start_mod_loop()

    def _start_mod_loop(self):
        def _mod_checker():
            while True:
                try:
                    time.sleep(10)
                    if self.current_tab == "MODS" and not self.mod_manager.cached_installed_mods:
                        if hasattr(self, 'app'):
                            self.app.invalidate()
                except Exception:
                    pass
        t = threading.Thread(target=_mod_checker, daemon=True)
        t.start()

    def _init_widgets(self):
        self.search_filter = TextArea(height=1, prompt=" Search: ", multiline=False)
        self.search_filter.buffer.on_text_changed += self._on_filter_change
        
        search_kb = KeyBindings()
        @search_kb.add('down')
        @search_kb.add('up')
        def _focus_list_from_search(event):
            if self.data_manager.filtered_servers:
                event.app.layout.focus(self.content_control)
        self.search_filter.control.key_bindings = search_kb

        self.nick_input = TextArea(
            height=1, multiline=False,
            text=str(self.data_manager.config.get("profile_name", DEFAULT_PROFILE_NAME) or "")
        )
        self.nick_input.buffer.on_text_changed += lambda _: self.data_manager.config.set("profile_name", self.nick_input.text)
        
        self.dayz_path_input = TextArea(
            height=1, multiline=False,
            text=str(self.data_manager.config.get("dayz_path", "") or "")
        )
        self.dayz_path_input.buffer.on_text_changed += lambda _: self.data_manager.config.set("dayz_path", self.dayz_path_input.text)

        mods_kb = KeyBindings()
        @mods_kb.add('right')
        def _mods_page_next(event):
            self.mod_manager.mods_page += 1
            event.app.invalidate()
        @mods_kb.add('left')
        def _mods_page_prev(event):
            if self.mod_manager.mods_page > 0:
                self.mod_manager.mods_page -= 1
            event.app.invalidate()

        self.installed_mods_control = FormattedTextControl(
            text=lambda: self.mod_manager.get_installed_mods_text(
                width=self.app.renderer.output.get_size().columns if hasattr(self, 'app') else 80
            ),
            focusable=True,
            key_bindings=mods_kb
        )

        self.launch_ok_btn = Button("OK", handler=self._close_launch)

        self.content_control = FormattedTextControl(
            text=self.get_server_list_text,
            focusable=True
        )
        self.content_window = Window(content=self.content_control, cursorline=False)
        
        self.mod_control = FormattedTextControl(text=self.get_mod_list_text)

    def _init_layout(self):
        self.main_content = VSplit([
            Frame(self.content_window, title="Server List"),
            Frame(Window(content=self.mod_control), title="Server Details", width=40),
        ])

        self.mods_content = Frame(
            Window(content=self.installed_mods_control),
            title="Mods"
        )
        
        self.settings_content = self.view_renderer.get_settings_view(
            self.nick_input, 
            self.dayz_path_input
        )

        def get_body():
            if self.current_tab == "SETTINGS":
                return self.settings_content
            elif self.current_tab == "MODS":
                return self.mods_content
            return self.main_content

        self.root_container = FloatContainer(
            content=HSplit([
                Frame(
                    self.search_filter,
                    title=f"{APP_NAME}"
                ),
                Window(content=FormattedTextControl(text=lambda: self.view_renderer.get_tabs_text(self.current_tab, self.tabs)), height=1),
                DynamicContainer(get_body), 
                Window(content=FormattedTextControl(text=lambda: self.view_renderer.get_footer_text()), height=1),
            ]),
            floats=[
                Float(content=ConditionalContainer(
                    content=self.get_launch_dialog(),
                    filter=Condition(lambda: self.show_launch_dialog)
                ))
            ]
        )

        self.app = Application(
            layout=Layout(self.root_container, focused_element=self.content_control),
            key_bindings=self.kb,
            mouse_support=True,
            full_screen=True,
        )


    def _close_launch(self):
        self.server_actions.cancel_launch() #d
        self.show_launch_dialog = False
        try:
            self.app.layout.focus(self.content_control)
        except:
            pass

    def refresh_data(self):
        def _worker():
            if not self.refresh_lock.acquire(blocking=False):
                return
            try:
                self.data_manager.loading = True
                if hasattr(self, 'app'): self.app.invalidate()
                self.data_manager.fetch_data(force=True)
                self.update_filtered()
            finally:
                self.data_manager.loading = False
                if hasattr(self, 'app'): self.app.invalidate()
                self.refresh_lock.release()

        threading.Thread(target=_worker, daemon=True).start()

    def _on_filter_change(self, buffer=None):
        self.selected_index = 0
        
        self.update_filtered()
        
        if self.current_tab == "GLOBAL":
            if self.search_timer:
                self.search_timer.cancel()
            
            def do_search():
                st = self.search_filter.text
                if len(st) >= 2 or (len(st) == 0 and self.data_manager.last_search_text):
                    self.data_manager.fetch_data(st)
                    self.update_filtered()
                    if hasattr(self, 'app'):
                        self.app.invalidate()

            self.search_timer = threading.Timer(0.6, do_search)
            self.search_timer.start()

    def update_filtered(self):
        self.data_manager.update_filtered(
            self.current_tab,
            self.search_filter.text
        )
        if self.selected_index >= len(self.data_manager.filtered_servers):
            self.selected_index = max(0, len(self.data_manager.filtered_servers) - 1)

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        self.selected_index = 0
        self.update_filtered()
        
        try:
            if tab_name == "SETTINGS":
                self.app.layout.focus(self.nick_input)
                self.nick_input.buffer.cursor_position = len(self.nick_input.text)
            elif tab_name == "MODS":
                self.mod_manager.clear_cache() #ref mods on entry
                self.app.layout.focus(self.installed_mods_control)
            else:
                self.app.layout.focus(self.content_control)
        except (ValueError, AttributeError):
            pass
            
        self.app.invalidate()

    def join_server_wrapper(self, server):
        def on_start(msg):
            self.launch_message = msg
            self.show_launch_dialog = True
            self.app.invalidate()
        
        def on_end(success, err):
            if not success:
                 self.launch_message = err
            else:
                 self.show_launch_dialog = False
                 try:
                     self.app.layout.focus(self.content_control)
                 except: pass
            
            self.app.invalidate()
            
        self.server_actions.join_server(server, on_start, on_end)

    def get_server_list_text(self):
        if not hasattr(self, 'app'): return ""
        size = self.app.renderer.output.get_size()
        return self.view_renderer.get_server_list_text(
             self.data_manager.filtered_servers,
             self.selected_index,
             self.data_manager.live_info,
             self.data_manager.loading,
             self.current_tab,
             (size.columns, size.rows),
             self.search_filter.text
        )
    
    def get_mod_list_text(self):
        server = None
        if self.data_manager.filtered_servers and self.selected_index < len(self.data_manager.filtered_servers):
            server = self.data_manager.filtered_servers[self.selected_index]
        
        live = None
        if server:
            live = self.data_manager.live_info.get((server.get('ip'), server.get('port')))
            
        return self.mod_manager.get_mod_list_text(server, live)

    def get_launch_dialog(self):
        return Shadow(
            body=Frame(
                HSplit([
                    Label(text=lambda: self.launch_message),
                ], padding=1),
                title="Launching Game",
                width=50,
            )
        )

    def run(self):
        try:
            with patch_stdout():
                try:
                    self.app.run()
                except (KeyboardInterrupt, EOFError):
                    pass
        finally:
            try:
                self.live_updater.stop()
            except:
                pass
            
            sys.stdout.write("\033[?1000l\033[?1002l\033[?1003l\033[?1004l\033[?1005l\033[?1006l\033[?1015l\033[?25h")
            sys.stdout.flush()

if __name__ == "__main__":
    tui = DayZLauncherTUI()
    tui.run()