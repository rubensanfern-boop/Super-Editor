'''Projeto Editor de Texto personalizado,
desenvolvido este ano de 2026 com vista 
a aprimorar a produtividade e a experiência do usuário.'''

# imports
import os
import re
from substituicoes import carregar_substituicoes

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter.font as tkFont

from pdfexporter import exportar_pdf_simples, md_para_texto
from temas.theme import carregar_tema


class EditorTexto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Super EDITOR")
        self.geometry("800x600")
        self.theme = "light"  # Tema padrão
        self.theme = carregar_tema(self.theme)
        self.focus_mode = False  # Modo de foco desativado por padrão
        self.current_font = ("Segoe UI", 12)  # Fonte padrão


        self.banner_focus = None
        self.focus_container = None
        self.focus_frame = None
        self.focus_text = None

        self._create_widgets()
        self._create_menu()

    # ---------------------------------------------------------
    # WIDGETS E INTERFACE
    # ---------------------------------------------------------
    def _fade_overlay(self, start=0, end=0.8, steps=10):
        largura = self.winfo_width()
        altura = self.winfo_height()
        x = self.winfo_rootx()
        y = self.winfo_rooty()

        overlay = tk.Toplevel(self)
        overlay.overrideredirect(True)
        overlay.geometry(f"{largura}x{altura}+{x}+{y}")
        overlay.lift()
        overlay.attributes("-alpha", start)
        overlay.configure(bg="black")

        def fade(i):
            alpha = start + (end - start) * (i / steps)
            overlay.attributes("-alpha", alpha)
            if i < steps:
                self.after(20, lambda: fade(i + 1))
            else:
                overlay.destroy()

        fade(0)

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        

        self.criar_aba()

        self.bind("<Control-n>", lambda e: self.novo_arquivo())
        self.bind("<Control-o>", lambda e: self.abrir_arquivo())
        self.bind("<Control-s>", lambda e: self.salvar_arquivo())
        self.bind("<Control-Shift-S>", lambda e: self.salvar_como())
        self.bind("<Control-q>", lambda e: self.sair())
        self.bind("<Control-z>", lambda e: self.desfazer())
        self.bind("<Control-y>", lambda e: self.refazer())
        self.bind("<Control-x>", lambda e: self.recortar())
        self.bind("<Control-c>", lambda e: self.copiar())
        self.bind("<Control-v>", lambda e: self.colar())
        self.bind("<Control-a>", lambda e: self.selecionar_tudo())
        self.bind_all("<Control-w>", lambda e: self.fechar_tab())
        self.bind("<F11>", lambda e: self.modo_focus())
        self.bind("<Control-plus>", lambda e: self.aumentar_tamanho())
        self.bind("<Control-minus>", lambda e: self.diminuir_tamanho())
        self.bind("<Control-0>", lambda e: self.reset_tamanho())

        self.status_bar = ttk.Label(self, text="Sem arquivo aberto", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------------------------------------------------------
    # MENU
    # ---------------------------------------------------------
    def _create_menu(self):
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Novo   Ctrl+N", command=self.novo_arquivo)
        file_menu.add_command(label="Abrir   Ctrl+O", command=self.abrir_arquivo)
        file_menu.add_command(label="Salvar   Ctrl+S", command=self.salvar_arquivo)
        file_menu.add_command(label="Salvar Como   Ctrl+Shift+S", command=self.salvar_como)
        file_menu.add_command(label="Exportar para PDF", command=self.exportar_pdf)
        file_menu.add_command(label="Fechar Aba    Ctrl+W", command=self.fechar_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Sair   Ctrl+Q", command=self.sair)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Desfazer   Ctrl+Z", command=self.desfazer)
        edit_menu.add_command(label="Refazer   Ctrl+Y", command=self.refazer)
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar   Ctrl+X", command=self.recortar)
        edit_menu.add_command(label="Copiar   Ctrl+C", command=self.copiar)
        edit_menu.add_command(label="Colar   Ctrl+V", command=self.colar)
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo   Ctrl+A", command=self.selecionar_tudo)
        edit_menu.add_command(label="Substituir Palavras (Dicionário)", command=self.substituir_palavras)
        edit_menu.add_command(label="Modo Focus   F11", command=self.modo_focus)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)

        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Tema Claro", command=lambda: self.mudar_tema("light"))
        theme_menu.add_command(label="Tema Escuro", command=lambda: self.mudar_tema("dark"))
        menu_bar.add_cascade(label="Tema", menu=theme_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Sobre",
            command=lambda: messagebox.showinfo(
                "Sobre",
                "Editor de Texto Personalizado\nDesenvolvido em 2026 por Rúben Fernandes.",
            ),
        )
        help_menu.add_command(label="Atalhos de Teclado", command=self.mostrar_atalhos)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)

        font_menu = tk.Menu(menu_bar, tearoff=0)
        font_menu.add_command(label="Segoe UI", command=lambda: self.mudar_fonte("Segoe UI"))
        font_menu.add_command(label="Arial", command=lambda: self.mudar_fonte("Arial"))
        font_menu.add_command(label="Times New Roman", command=lambda: self.mudar_fonte("Times New Roman"))
        font_menu.add_command(label="Consolas", command=lambda: self.mudar_fonte("Consolas"))
        font_menu.add_command(label="Courier New", command=lambda: self.mudar_fonte("Courier New"))
        font_menu.add_command(label="JetBrains Mono", command=lambda: self.mudar_fonte("JetBrains Mono"))
        menu_bar.add_cascade(label="Fonte", menu=font_menu)

        size_menu = tk.Menu(menu_bar, tearoff=0)
        size_menu.add_command(label="Aumentar   Ctrl++", command=self.aumentar_tamanho)
        size_menu.add_command(label="Diminuir   Ctrl+-", command=self.diminuir_tamanho)
        size_menu.add_command(label="Reset   Ctrl+0", command=self.reset_tamanho)
        menu_bar.add_cascade(label="Tamanho", menu=size_menu)

        self.config(menu=menu_bar)

    # ---------------------------------------------------------
    # TABS
    # ---------------------------------------------------------
    def criar_aba(self, nome="Sem Título"):
        frame = ttk.Frame(self.notebook)

        scroll_bar = ttk.Scrollbar(frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        widget_text = tk.Text(
            frame,
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            yscrollcommand=scroll_bar.set,
        )
        widget_text.pack(fill=tk.BOTH, expand=True)
        widget_text.config(font=self.current_font)
        scroll_bar.config(command=widget_text.yview)

        widget_text.tag_config("highlight", background="#fff59d")

        widget_text.bind("<Key>", self._evento_teclado)

        frame.text_widget = widget_text
        frame.current_file = None
        frame.modified = False

        # ---- TAB HEADER ----
        self.notebook.add(frame, text=f"{nome}")
        self.notebook.select(frame)

       

    # ---------------------------------------------------------
    # FUNÇÕES DE ARQUIVO
    # ---------------------------------------------------------
    def _evento_teclado(self, event):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        self.atualizar_contador(event)
        self._auto_substituir_palavra(event)
        self.marcar_aba_modificada(current_frame)

    def novo_arquivo(self):
        self.criar_aba()
        self.status_bar.config(text="Novo arquivo")
        self.atualizar_contador()

    def abrir_arquivo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                self.criar_aba(os.path.basename(file_path))
                current_frame = self.notebook.nametowidget(self.notebook.select())
                current_frame.text_widget.delete("1.0", tk.END)
                current_frame.text_widget.insert(tk.END, content)
                current_frame.current_file = file_path

                self.status_bar.config(text=f"Abrindo: {os.path.basename(file_path)}")
                current_frame.modified = False
                self.notebook.tab(current_frame, text=os.path.basename(file_path))
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
        current_frame.text_widget.edit_modified(False)
        self.marcar_aba_modificada()

    def salvar_arquivo(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        if current_frame.current_file:
            try:
                with open(current_frame.current_file, "w", encoding="utf-8") as file:
                    file.write(current_frame.text_widget.get("1.0", tk.END))
                self.status_bar.config(text=f"Salvo: {os.path.basename(current_frame.current_file)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
        else:
            self.salvar_como()
        current_frame.modified = False
        self.status_bar.config(text="Pronto!")
        nome = os.path.basename(current_frame.current_file)
        self.notebook.tab(current_frame, text=nome)

    def salvar_como(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(current_frame.text_widget.get("1.0", tk.END))

                current_frame.current_file = file_path
                self.notebook.tab(current_frame, text=os.path.basename(file_path))
                self.status_bar.config(text=f"Salvo como: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
        current_frame.text_widget.edit_modified(False)
        self.marcar_aba_modificada()

    def sair(self): # Fecha o editor, solicitando ao usuário para salvar alterações não salvas antes de sair
        current_frame = self.notebook.nametowidget(self.notebook.select())
        text_widget = current_frame.text_widget

        if text_widget.edit_modified():
            if messagebox.askyesno("Confirmar", "Deseja salvar o arquivo atual antes de sair?"):
                self.salvar_arquivo()
        self.destroy()

    def exportar_pdf(self): # Exporta o conteúdo da aba atual para um arquivo PDF
        current_frame = self.notebook.nametowidget(self.notebook.select())
        texto = current_frame.text_widget.get("1.0", "end-1c")
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )

        if caminho:
            texto_convertido = md_para_texto(texto)
            exportar_pdf_simples(texto_convertido, caminho)

    def fechar_tab(self): # Fecha a aba atualmente selecionada no editor
        aba_atual = self.notebook.select()
        if aba_atual:
            self.notebook.forget(aba_atual)

    def substituir_palavras(self): # Substitui automaticamente palavras no texto da aba atual com base nas substituições carregadas
        subs = carregar_substituicoes()
        current_frame = self.notebook.nametowidget(self.notebook.select())
        texto = current_frame.text_widget.get("1.0", "end-1c")

        todas_subs = {}
        for categoria in subs.values():
            todas_subs.update(categoria)

        for errado, correto in todas_subs.items():
            padrao = rf'(?<!\w){re.escape(errado)}(?!\w)'
            texto = re.sub(padrao, correto, texto, flags=re.IGNORECASE)

        current_frame.text_widget.delete("1.0", "end")
        current_frame.text_widget.insert("1.0", texto)

    def procurar_substituir(self): # Abre uma janela para procurar e substituir palavras no texto da aba atual
        janela = tk.Toplevel(self)
        janela.title("Procurar e Substituir")
        janela.geometry("300x150")

        tk.Label(janela, text="Procurar:").pack()
        entrada_procurar = tk.Entry(janela)
        entrada_procurar.pack()

        tk.Label(janela, text="Substituir por:").pack()
        entrada_substituir = tk.Entry(janela)
        entrada_substituir.pack()

        def aplicar(): # Aplica a substituição de palavras no texto da aba atual
            current_frame = self.notebook.nametowidget(self.notebook.select())
            procurar = entrada_procurar.get()
            substituir = entrada_substituir.get()

            texto = current_frame.text_widget.get("1.0", "end-1c")
            padrao = r"\b" + re.escape(procurar) + r"\b"
            texto = re.sub(padrao, substituir, texto)

            current_frame.text_widget.delete("1.0", "end")
            current_frame.text_widget.insert("1.0", texto)

            janela.destroy()

        tk.Button(janela, text="Aplicar", command=aplicar).pack(pady=10)

    def aplicar_tema(self): # Aplica o tema atual às abas e widgets do editor
        tema = self.tema

        style = ttk.Style()
        style.configure("TNotebook", background=tema["tab_bg"])
        style.configure("TNotebook.Tab", background=tema["tab_bg"], foreground=tema["tab_fg"])
        style.map(
            "TNotebook.Tab",
            background=[("selected", tema["bg"])],
            foreground=[("selected", tema["fg"])],
        )

        for tab in self.notebook.tabs():
            frame = self.notebook.nametowidget(tab)
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.config(
                        bg=tema["bg"],
                        fg=tema["fg"],
                        insertbackground=tema["insert"],
                        selectbackground=tema["select_bg"],
                        selectforeground=tema["select_fg"],
                    )

    def mudar_tema(self, novo_tema): # Altera o tema atual para o novo tema especificado e aplica as alterações
        self.tema_atual = novo_tema
        self.tema = carregar_tema(novo_tema)
        self.aplicar_tema()

    def _auto_substituir_palavra(self, event): # Substitui automaticamente palavras conforme as substituições carregadas
        tecla = event.keysym

        if tecla not in ("space", "Return", "Tab", "comma", "period", "semicolon", "colon"):
            return

        subs = carregar_substituicoes()

        todas_subs = {}
        for categoria in subs.values():
            todas_subs.update(categoria)

        current_frame = self.notebook.nametowidget(self.notebook.select())
        text_widget = current_frame.text_widget

        pos = text_widget.index("insert-1c")
        palavra_inicio = text_widget.index(f"{pos} wordstart")
        palavra_fim = text_widget.index(f"{pos} wordend")

        palavra = text_widget.get(palavra_inicio, palavra_fim)

        for errado, correto in todas_subs.items(): 
            if palavra.lower() == errado.lower():
                text_widget.tag_add("highlight", palavra_inicio, palavra_fim)

                def substituir():
                    text_widget.tag_remove("highlight", palavra_inicio, palavra_fim)
                    text_widget.delete(palavra_inicio, palavra_fim)
                    text_widget.insert(palavra_inicio, correto)
                    current_frame.modified = True

                text_widget.after(200, substituir)
                break

    def marcar_aba_modificada(self, frame): # Marca a aba como modificada, adicionando um indicador visual e atualizando a barra de status
        if not frame.modified:
            nome = self.notebook.tab(frame, "text")
            self.notebook.tab(frame, text="✎" + nome)
            frame.modified = True
            self.status_bar.config(text="Modificado")

    # ---------------- MODO FOCUS ----------------
    def _remover_banner_focus(self): # Remove o banner do modo focus, se estiver presente
        if self.banner_focus is not None:
            self.banner_focus.destroy()
            self.banner_focus = None

    def modo_focus(self): # Alterna o modo focus, ativando ou desativando conforme o estado atual
        self.focus_mode = not self.focus_mode

        if self.focus_mode:
            self._ativar_focus()
            self._fade_overlay(start=0, end=0.8)
        else:
            self._desativar_focus()
            self._fade_overlay(start=0.8, end=0)

    def _ativar_focus(self): # Ativa o modo focus, ocultando a interface normal e exibindo o Text em foco
        self.config(menu="")
        self.status_bar.pack_forget()
        self.main_frame.pack_forget()

        self._remover_banner_focus()
        self.banner_focus = tk.Label(
            self,
            text="🧘 MODO FOCUS ATIVO",
            bg="#222",
            fg="#00ff88",
            font=("Segoe UI", 14, "bold"),
            anchor="center",
        )
        self.banner_focus.pack(side="top", fill=tk.X)

        self.focus_container = ttk.Frame(self)
        self.focus_container.pack(side="top", fill=tk.BOTH, expand=True)

        self.focus_frame = ttk.Frame(self.focus_container)
        self.focus_frame.pack(fill=tk.BOTH, expand=True)

        current_frame = self.notebook.nametowidget(self.notebook.select())
        self.focus_text = tk.Text(self.focus_frame, wrap=tk.WORD, undo=True)
        self.focus_text.pack(fill=tk.BOTH, expand=True)

        texto = current_frame.text_widget.get("1.0", tk.END)
        self.focus_text.insert("1.0", texto)

        self.focus_text.bind("<Key>", lambda e: self._sync_focus_text())

    def _desativar_focus(self): # Desativa o modo focus e restaura a interface normal
        self._remover_banner_focus()

        if self.focus_container is not None:
            self.focus_container.destroy()
            self.focus_container = None

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._create_menu()

    def _sync_focus_text(self): # Sincroniza o conteúdo do Text do modo focus com a aba atual
        current_frame = self.notebook.nametowidget(self.notebook.select())
        texto = self.focus_text.get("1.0", tk.END)
        current_frame.text_widget.delete("1.0", tk.END)
        current_frame.text_widget.insert("1.0", texto)
        current_frame.modified = True

    
    # ---------------------------------------------------------
    # FONTE E TAMANHO
    # ---------------------------------------------------------
    def mudar_fonte(self, nome_fonte): # Muda a fonte atual para o nome especificado
        self.current_font = (nome_fonte, self.current_font[1])

        for tab in self.notebook.tabs():
            frame = self.notebook.nametowidget(tab)
            frame.text_widget.config(font=self.current_font)

        if self.focus_mode and self.focus_text is not None:
            self.focus_text.config(font=self.current_font)

    def aumentar_tamanho(self): # Aumenta o tamanho da fonte em 1
        tamanho = self.current_font[1] + 1
        self.current_font = (self.current_font[0], tamanho)
        self._aplicar_tamanho()

    def diminuir_tamanho(self): # Diminui o tamanho da fonte em 1, mantendo um mínimo de 8
        tamanho = max(8, self.current_font[1] - 1)
        self.current_font = (self.current_font[0], tamanho)
        self._aplicar_tamanho()

    def reset_tamanho(self): # Reseta o tamanho da fonte para o valor padrão (12)
        self.current_font = (self.current_font[0], 12)
        self._aplicar_tamanho()

    def _aplicar_tamanho(self): # Aplica o tamanho de fonte atual a todas as abas e ao modo de foco, se ativo
        for tab in self.notebook.tabs():
            frame = self.notebook.nametowidget(tab)
            frame.text_widget.config(font=self.current_font)

        if self.focus_mode and self.focus_text is not None:
            self.focus_text.config(font=self.current_font)

    def fechar_tab_costum(self, frame): # Fecha a aba personalizada com o botão de fechar
        self.notebook.forget(frame)


    #---------------------------------------------------------
    # Funções de edição
    #---------------------------------------------------------
    def desfazer(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.edit_undo()

    def refazer(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.edit_redo()

    def recortar(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.event_generate("<<Cut>>")

    def copiar(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.event_generate("<<Copy>>")

    def colar(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.event_generate("<<Paste>>")

    def selecionar_tudo(self):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        current_frame.text_widget.tag_add("sel", "1.0", "end")

    def mostrar_atalhos(self):
        atalhos = (
            "Atalhos de Teclado:\n\n"
            "Novo Arquivo: Ctrl+N\n"
            "Abrir Arquivo: Ctrl+O\n"
            "Salvar Arquivo: Ctrl+S\n"
            "Salvar Como: Ctrl+Shift+S\n"
            "Exportar para PDF: (Menu Arquivo)\n"
            "Fechar Aba: Ctrl+W\n"
            "Sair: Ctrl+Q\n"
            "Desfazer: Ctrl+Z\n"
            "Refazer: Ctrl+Y\n"
            "Recortar: Ctrl+X\n"
            "Copiar: Ctrl+C\n"
            "Colar: Ctrl+V\n"
            "Selecionar Tudo: Ctrl+A\n"
        )
        messagebox.showinfo("Atalhos de Teclado", atalhos)

    # ---------------------------------------------------------
    # CONTADOR DE PALAVRAS
    # ---------------------------------------------------------
    def atualizar_contador(self, event=None):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        texto = current_frame.text_widget.get("1.0", tk.END).strip()

        palavras = len(texto.split())
        caracteres = len(texto)

        if current_frame.current_file:
            nome = os.path.basename(current_frame.current_file)
            self.status_bar.config(text=f"{nome} | Palavras: {palavras} | Caracteres: {caracteres}")
        else:
            self.status_bar.config(text=f"Sem arquivo aberto | Palavras: {palavras} | Caracteres: {caracteres}")

    # ---------------------------------------------------------
    def run(self):
        self.mainloop()


if __name__ == "__main__":
    editor = EditorTexto()
    editor.run()





