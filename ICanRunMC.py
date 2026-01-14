import customtkinter as ctk
import threading
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppMesa(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ICanRunMC")
        self.geometry("500x480")
        self.resizable(False, False)

        self.variables = [
            "MESA_GL_VERSION_OVERRIDE=3.3COMPAT",
            "MESA_GLSL_VERSION_OVERRIDE=330",
            "MESA_NO_ERROR=1",
            "MESA_GLES_VERSION_OVERRIDE=3.1"
        ]
        self.tag_inicio = "# --- MESA OPTIMIZATION START ---"
        self.tag_fin = "# --- MESA OPTIMIZATION END ---"

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_title = ctk.CTkLabel(self.main_frame, text="ICanRunMC", 
                                        font=ctk.CTkFont(size=22, weight="bold"))
        self.label_title.pack(pady=(20, 5))

        self.info_box = ctk.CTkTextbox(self.main_frame, width=400, height=120, corner_radius=10)
        self.info_box.pack(pady=10)
        self.info_box.insert("0.0", "Parámetros que se aplicaran:\n\n" + "\n".join(self.variables))
        self.info_box.configure(state="disabled")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.btn_aplicar = ctk.CTkButton(self.main_frame, text="Aplicar parámetros", 
                                         command=lambda: self.ejecutar("aplicar"),
                                         height=40, corner_radius=8, fg_color="#1f538d")
        self.btn_aplicar.pack(pady=5)

        self.btn_revertir = ctk.CTkButton(self.main_frame, text="Revertir cambios", 
                                          command=lambda: self.ejecutar("revertir"),
                                          height=40, corner_radius=8, fg_color="#a11d1d", hover_color="#7a1515")
        self.btn_revertir.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Script by Negal75 and GUI by Ars-byte :b.", font=("Arial", 12))
        self.status_label.pack(pady=(10, 10))

    def ejecutar(self, modo):
        if os.geteuid() != 0:
            self.status_label.configure(text="ERROR: Ejecuta con 'sudo python3 ...'", text_color="#ff4444")
            return

        self.btn_aplicar.configure(state="disabled")
        self.btn_revertir.configure(state="disabled")
        
        if modo == "aplicar":
            threading.Thread(target=self.logic_aplicar).start()
        else:
            threading.Thread(target=self.logic_revertir).start()

    def logic_aplicar(self):
        try:
            self.status_label.configure(text="Leyendo configuración...", text_color="white")
            with open("/etc/environment", "r") as f:
                content = f.read()

            if self.tag_inicio in content:
                self.status_label.configure(text="Los cambios ya están aplicados.", text_color="#ffbb00")
            else:
                self.status_label.configure(text="Escribiendo cambios...")
                self.progress_bar.set(0.6)
                with open("/etc/environment", "a") as f:
                    f.write(f"\n{self.tag_inicio}\n")
                    for var in self.variables:
                        f.write(f"export {var}\n")
                    f.write(f"{self.tag_fin}\n")
                self.status_label.configure(text="¡Éxito! Reinicia el sistema.", text_color="#28a745")
            
            self.progress_bar.set(1.0)
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="#ff4444")
        finally:
            self.reset_btns()

    def logic_revertir(self):
        try:
            self.status_label.configure(text="Buscando cambios para eliminar...")
            with open("/etc/environment", "r") as f:
                lines = f.readlines()

            new_lines = []
            skip = False
            found = False
            for line in lines:
                if self.tag_inicio in line:
                    skip = True
                    found = True
                    continue
                if self.tag_fin in line:
                    skip = False
                    continue
                if not skip:
                    new_lines.append(line)

            if found:
                with open("/etc/environment", "w") as f:
                    f.writelines(new_lines)
                self.status_label.configure(text="Cambios eliminados con éxito.", text_color="#28a745")
            else:
                self.status_label.configure(text="No se encontraron cambios previos.", text_color="#ffbb00")
            
            self.progress_bar.set(1.0)
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="#ff4444")
        finally:
            self.reset_btns()

    def reset_btns(self):
        self.btn_aplicar.configure(state="normal")
        self.btn_revertir.configure(state="normal")

if __name__ == "__main__":
    app = AppMesa()
    app.mainloop()