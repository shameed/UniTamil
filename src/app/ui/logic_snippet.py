
# In MainWindow class...

    def __init__(self, page: ft.Page, pipeline: ProcessingPipeline = None):
        # ... existing ...
        self.stop_event = threading.Event()
        self.is_processing = False
        self.reset_btn_ref = ft.Ref[ft.ElevatedButton]()
        # ... existing ...

    def on_reset_stop_click(self, e):
        if self.is_processing:
             # STOP MODE
             self.confirm_dialog("Stop Processing?", "Are you sure you want to stop processing?", self.confirm_stop)
        else:
             # RESET MODE
             self.confirm_dialog("Reset Application?", "This will clear all selections and logs. Continue?", self.confirm_reset)

    def confirm_dialog(self, title, msg, action):
        def close_dlg(e):
             self.page.dialog.open = False
             self.page.update()
             if e.control.text == "Yes":
                 action()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(msg),
            actions=[
                ft.TextButton("No", on_click=close_dlg),
                ft.TextButton("Yes", on_click=close_dlg, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def confirm_stop(self):
        self.log("Stopping...")
        self.stop_event.set()
        # Button state will update when pipeline finishes/exits

    def confirm_reset(self):
        self.selected_input_dir = None
        self.selected_output_dir = None
        self.input_dir_text.value = ""
        self.output_dir_text.value = ""
        self.files_list.controls.clear()
        self.file_cards.clear()
        self.log_view_ref.current.controls.clear()
        self.meta_total_files.value = "Total Files: --"
        self.meta_last_mod.value = "Status: Idle"
        self.check_ready() # Disables Start
        self.update()
        
    def start_processing(self, e):
        # ...
        self.is_processing = True
        self.stop_event.clear()
        self._update_reset_stop_btn(True) # Become Stop
        # ...

    def _update_reset_stop_btn(self, processing):
        if self.reset_btn_ref.current:
            btn = self.reset_btn_ref.current
            if processing:
                btn.text = "Stop Processing"
                btn.style.bgcolor = ft.colors.RED_500
            else:
                btn.text = "Reset Application"
                btn.style.bgcolor = ft.colors.GREY_500
            btn.update()
            
    # In run_parallel_pipeline main loop...
        # ...
        if self.stop_event.is_set():
             self.log("Processing Stopped by User.")
             return # Exit
        # ...
        
    # Finally block or end of run...
        self.is_processing = False
        self._update_reset_stop_btn(False) # Become Reset
