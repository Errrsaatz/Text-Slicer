# Copyright (C) 2025 [Boris HANICOTTE]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You can check the full license text at the following URL:
# https://www.gnu.org/licenses/gpl-3.0.html

import os
import re
import json
import tkinter as tk
from tkinter import filedialog, StringVar, IntVar, BooleanVar
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import *

class TextSlicerApp:
    def __init__(self, root):
        self.root = root
        
        # Création des dossiers nécessaires s'ils n'existent pas
        self.create_required_folders()
        
        # Chargement ou création de la configuration
        self.load_or_create_config()
        
        # Thèmes disponibles (liste complète)
        self.available_themes = ["morph", "minty", "simplex", "journal", "cerculean", "yeti", "sandstone", 
                               "lumen", "solar", "united", "cyborg", "cosmo", "vapor", "pulse", 
                               "superhero", "litera", "darkly", "flatly"]
        
        # Découvrir les langues disponibles
        self.available_languages = self.discover_available_languages()
        
        # Variables
        self.input_file_path = StringVar()
        self.average_words = IntVar(value=self.config.get("default_average_words", 500))
        self.max_words = IntVar(value=self.config.get("default_max_words", 1000))
        self.file_prefix = StringVar(value=self.config.get("default_file_prefix", "part"))
        self.output_folder = StringVar(value=self.config.get("last_output_directory", os.path.join(os.path.dirname(__file__), "temp")))
        self.preserve_newlines = BooleanVar(value=False)
        self.cut_at_newline = BooleanVar(value=False)
        
        # Langue et thème
        lang_code = self.config.get("language", "en")  # Défaut en anglais si aucune langue n'est spécifiée
        if lang_code in [code for _, code in self.available_languages.items()]:
            self.language = StringVar(value=self.get_language_name(lang_code))
        else:
            # Si le code de langue dans la config n'est pas disponible, utiliser la première langue disponible
            if self.available_languages:
                first_lang = next(iter(self.available_languages.keys()))
                self.language = StringVar(value=first_lang)
                lang_code = self.available_languages[first_lang]
            else:
                # Fallback en anglais si aucune langue n'est disponible
                self.language = StringVar(value="English")
                lang_code = "en"
                # Créer un fichier de langue anglais par défaut
                self.create_default_english_language_file()
        
        self.theme = StringVar(value=self.config.get("theme", "darkly"))
        
        # Charger les traductions
        self.load_language(lang_code)
        
        # Configurer l'interface
        self.root.title(self.translations.get("app_title", "Text Slicer"))
        self.root.geometry("750x650")  # Augmenté pour accommoder les nouveaux contrôles
        
        # Création de l'interface
        self.create_widgets()
        
        # Configurer les callbacks pour les changements de langue et de thème
        self.language.trace_add("write", self.on_language_change)
        self.theme.trace_add("write", self.on_theme_change)
    
    def create_required_folders(self):
        """Crée les dossiers nécessaires s'ils n'existent pas"""
        # Dossier de configuration
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Dossier des langues
        lang_dir = os.path.join(os.path.dirname(__file__), "languages")
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        # Dossier temporaire pour les fichiers de sortie
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    
    def discover_available_languages(self):
        """Découvre les langues disponibles en scannant le dossier languages"""
        languages = {}
        lang_dir = os.path.join(os.path.dirname(__file__), "languages")
        
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        # Parcourir tous les fichiers JSON dans le dossier languages
        for filename in os.listdir(lang_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(lang_dir, filename), "r", encoding="utf-8") as f:
                        lang_data = json.load(f)
                        metadata = lang_data.get("metadata", {})
                        lang_name = metadata.get("lang", "Unknown")
                        lang_code = filename[:-5]  # Enlever l'extension .json
                        languages[lang_name] = lang_code
                except Exception as e:
                    print(f"Error loading language file {filename}: {e}")
        
        # Trier les langues par ordre alphabétique
        return dict(sorted(languages.items()))
    
    def create_default_english_language_file(self):
        """Crée un fichier de langue anglais par défaut si aucune langue n'est disponible"""
        lang_dir = os.path.join(os.path.dirname(__file__), "languages")
        en_file = os.path.join(lang_dir, "en.json")
        
        default_english = {
            "metadata": {
                "lang": "English",
                "author": "System",
                "created": "2025-04-14",
                "version": "1.0",
                "comment": "Default English language file"
            },
            "translations": {
                "app_title": "Text Slicer",
                "main_tab": "Text Slicer",
                "settings_tab": "Settings",
                "file_selection": "File Selection",
                "browse": "Browse",
                "clear": "Clear",
                "output_folder": "Output Folder",
                "parameters": "Parameters",
                "avg_words": "Average words per file:",
                "max_words": "Maximum words per file:",
                "file_name": "File names:",
                "options": "Options",
                "preserve_newlines": "Preserve newlines",
                "cut_at_newline": "Cut at next newline after average word count",
                "slice_button": "Slice",
                "error_no_file": "Error: No file selected.",
                "error_file_not_exist": "Error: The file {file} does not exist.",
                "success_message": "The text has been divided into {count} files in the folder '{folder}'.",
                "language": "Language:",
                "theme": "Theme:",
                "appearance": "Appearance",
                "about": "About",
                "app_description": "An application to split text files into multiple parts based on word count.",
                "created_by": "Created by Boris Hanicotte",
                "translation_info": "Translation Information",
                "translator": "Translator",
                "version": "Version",
                "created": "Created on",
                "comment": "Comment",
                "translation_note": "Select your preferred language from the menu above."
            }
        }
        
        try:
            with open(en_file, "w", encoding="utf-8") as f:
                json.dump(default_english, f, indent=2)
            # Ajouter cette langue à la liste des langues disponibles
            self.available_languages = {"English": "en"}
        except Exception as e:
            print(f"Error creating default English language file: {e}")
            # Fallback en mémoire
            self.available_languages = {"English": "en"}

    def load_or_create_config(self):
        """Charge la configuration ou crée un fichier par défaut"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.create_default_config(config_path)
        else:
            self.create_default_config(config_path)
    
    def create_default_config(self, config_path):
        """Crée un fichier de configuration par défaut"""
        self.config = {
            "language": "en",
            "theme": "darkly",
            "last_input_directory": "",
            "last_output_directory": os.path.join(os.path.dirname(__file__), "temp"),
            "default_average_words": 500,
            "default_max_words": 1000,
            "default_file_prefix": "part"
        }
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
        
        # Mettre à jour la configuration avec les valeurs actuelles
        self.config["language"] = self.available_languages[self.language.get()]
        self.config["theme"] = self.theme.get()
        self.config["default_average_words"] = self.average_words.get()
        self.config["default_max_words"] = self.max_words.get()
        self.config["default_file_prefix"] = self.file_prefix.get()
        self.config["last_output_directory"] = self.output_folder.get()
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_language_name(self, lang_code):
        """Obtient le nom de la langue à partir du code"""
        for name, code in self.available_languages.items():
            if code == lang_code:
                return name
        return list(self.available_languages.keys())[0] if self.available_languages else "English"
    
    def load_language(self, lang_code):
        """Charge les traductions pour la langue spécifiée"""
        try:
            lang_file = os.path.join(os.path.dirname(__file__), "languages", f"{lang_code}.json")
            with open(lang_file, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
                self.current_language_metadata = lang_data.get("metadata", {})
                self.translations = lang_data.get("translations", {})
        except Exception as e:
            print(f"Error loading language file: {e}")
            # Fallback to default translations
            self.current_language_metadata = {
                "lang": "English",
                "author": "System",
                "created": "2025-04-14",
                "version": "1.0"
            }
            self.translations = {
                "app_title": "Text Slicer",
                "main_tab": "Text Slicer",
                "settings_tab": "Settings",
                "file_selection": "File Selection",
                "browse": "Browse",
                "clear": "Clear",
                "output_folder": "Output Folder",
                "parameters": "Parameters",
                "avg_words": "Average words per file:",
                "max_words": "Maximum words per file:",
                "file_name": "File names:",
                "options": "Options",
                "preserve_newlines": "Preserve newlines",
                "cut_at_newline": "Cut at next newline after average word count",
                "slice_button": "Slice",
                "error_no_file": "Error: No file selected.",
                "error_file_not_exist": "Error: The file {file} does not exist.",
                "success_message": "The text has been divided into {count} files in the folder '{folder}'.",
                "language": "Language:",
                "theme": "Theme:",
                "appearance": "Appearance",
                "about": "About",
                "app_description": "An application to split text files into multiple parts based on word count.",
                "created_by": "Created by Boris Hanicotte",
                "translation_info": "Translation Information",
                "translator": "Translator",
                "version": "Version",
                "created": "Created on",
                "comment": "Comment",
                "translation_note": "Select your preferred language from the menu above."
            }
    
    def on_language_change(self, *args):
        """Callback pour le changement de langue"""
        lang_code = self.available_languages[self.language.get()]
        self.load_language(lang_code)
        self.update_ui_text()
        self.save_config()
    
    def on_theme_change(self, *args):
        """Callback pour le changement de thème"""
        new_theme = self.theme.get()
        self.root.style.theme_use(new_theme)
        self.save_config()
    
    def update_ui_text(self):
        """Met à jour tous les textes de l'interface avec la langue actuelle"""
        self.root.title(self.translations.get("app_title", "Text Slicer"))
        
        # Mettre à jour les textes des onglets
        self.notebook.tab(0, text=self.translations.get("main_tab", "Text Slicer"))
        self.notebook.tab(1, text=self.translations.get("settings_tab", "Settings"))
        
        # Mettre à jour les textes des widgets de l'onglet principal
        self.file_frame.configure(text=self.translations.get("file_selection", "File Selection"))
        self.browse_button.configure(text=self.translations.get("browse", "Browse"))
        self.clear_button.configure(text=self.translations.get("clear", "Clear"))
        
        self.output_frame.configure(text=self.translations.get("output_folder", "Output Folder"))
        self.output_browse_button.configure(text=self.translations.get("browse", "Browse"))
        
        self.params_frame.configure(text=self.translations.get("parameters", "Parameters"))
        self.avg_label.configure(text=self.translations.get("avg_words", "Average words per file:"))
        self.max_label.configure(text=self.translations.get("max_words", "Maximum words per file:"))
        self.prefix_label.configure(text=self.translations.get("file_name", "File names:"))
        
        self.options_frame.configure(text=self.translations.get("options", "Options"))
        self.preserve_newlines_check.configure(text=self.translations.get("preserve_newlines", "Preserve newlines"))
        self.cut_newline_check.configure(text=self.translations.get("cut_at_newline", "Cut at next newline after average word count"))
        
        self.slice_button.configure(text=self.translations.get("slice_button", "Slice"))
        
        # Mettre à jour les textes des widgets de l'onglet configuration
        self.appearance_frame.configure(text=self.translations.get("appearance", "Appearance"))
        self.lang_label.configure(text=self.translations.get("language", "Language:"))
        self.theme_label.configure(text=self.translations.get("theme", "Theme:"))
        
        self.about_frame.configure(text=self.translations.get("about", "About"))
        self.app_description.configure(text=self.translations.get("app_description", 
            "An application to split text files into multiple parts based on word count."))
        self.author_label.configure(text=self.translations.get("created_by", "Created by Boris Hanicotte"))
        
        self.translation_info_title.configure(text=self.translations.get("translation_info", "Translation Information"))
        self.translation_note.configure(text=self.translations.get("translation_note", 
            "Select your preferred language from the menu above."))
        
        # Mettre à jour les informations de traduction
        self.update_translation_info()

    def create_widgets(self):
        # Création du notebook (onglets)
        self.notebook = Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Onglet principal - Text Slicer
        main_tab = Frame(self.notebook, padding=10)
        self.notebook.add(main_tab, text=self.translations.get("main_tab", "Text Slicer"))
        
        # Onglet paramètres
        settings_tab = Frame(self.notebook, padding=10)
        self.notebook.add(settings_tab, text=self.translations.get("settings_tab", "Settings"))
        
        # ===== ONGLET PRINCIPAL =====
        
        # Section sélection de fichier
        self.file_frame = LabelFrame(main_tab, text=self.translations.get("file_selection", "File Selection"), padding=10)
        self.file_frame.pack(fill=X, pady=10)
        
        file_entry = Entry(self.file_frame, textvariable=self.input_file_path, width=50)
        file_entry.pack(side=LEFT, padx=5, fill=X, expand=YES)
        
        self.browse_button = Button(self.file_frame, text=self.translations.get("browse", "Browse"), command=self.browse_file)
        self.browse_button.pack(side=LEFT, padx=5)
        
        self.clear_button = Button(self.file_frame, text=self.translations.get("clear", "Clear"), command=self.clear_file_path)
        self.clear_button.pack(side=LEFT, padx=5)
        
        # Section dossier de sortie
        self.output_frame = LabelFrame(main_tab, text=self.translations.get("output_folder", "Output Folder"), padding=10)
        self.output_frame.pack(fill=X, pady=10)
        
        output_entry = Entry(self.output_frame, textvariable=self.output_folder, width=50)
        output_entry.pack(side=LEFT, padx=5, fill=X, expand=YES)
        
        self.output_browse_button = Button(self.output_frame, text=self.translations.get("browse", "Browse"), command=self.browse_output_folder)
        self.output_browse_button.pack(side=LEFT, padx=5)
        
        # Section paramètres
        self.params_frame = LabelFrame(main_tab, text=self.translations.get("parameters", "Parameters"), padding=10)
        self.params_frame.pack(fill=X, pady=10)
        
        # Moyenne de mots
        avg_frame = Frame(self.params_frame)
        avg_frame.pack(fill=X, pady=5)
        self.avg_label = Label(avg_frame, text=self.translations.get("avg_words", "Average words per file:"))
        self.avg_label.pack(side=LEFT, padx=5)
        Entry(avg_frame, textvariable=self.average_words, width=10).pack(side=LEFT, padx=5)
        
        # Maximum de mots
        self.max_frame = Frame(self.params_frame)
        self.max_frame.pack(fill=X, pady=5)
        self.max_label = Label(self.max_frame, text=self.translations.get("max_words", "Maximum words per file:"))
        self.max_label.pack(side=LEFT, padx=5)
        self.max_entry = Entry(self.max_frame, textvariable=self.max_words, width=10)
        self.max_entry.pack(side=LEFT, padx=5)
        
        # Préfixe des fichiers
        prefix_frame = Frame(self.params_frame)
        prefix_frame.pack(fill=X, pady=5)
        self.prefix_label = Label(prefix_frame, text=self.translations.get("file_name", "File names:"))
        self.prefix_label.pack(side=LEFT, padx=5)
        Entry(prefix_frame, textvariable=self.file_prefix, width=20).pack(side=LEFT, padx=5)
        Label(prefix_frame, text="_XXXX.txt").pack(side=LEFT, padx=5)
        
        # Options supplémentaires
        self.options_frame = LabelFrame(main_tab, text=self.translations.get("options", "Options"), padding=10)
        self.options_frame.pack(fill=X, pady=10)
        
        # Préserver les retours à la ligne
        self.preserve_newlines_check = Checkbutton(
            self.options_frame, 
            text=self.translations.get("preserve_newlines", "Preserve newlines"), 
            variable=self.preserve_newlines
        )
        self.preserve_newlines_check.pack(anchor=W, pady=5)
        
        # Couper au prochain saut de ligne après average_words
        self.cut_newline_check = Checkbutton(
            self.options_frame, 
            text=self.translations.get("cut_at_newline", "Cut at next newline after average word count"), 
            variable=self.cut_at_newline, 
            command=self.toggle_max_words
        )
        self.cut_newline_check.pack(anchor=W, pady=5)
        
        # Bouton pour découper
        self.slice_button = Button(
            main_tab, 
            text=self.translations.get("slice_button", "Slice"), 
            command=self.slice_text, 
            bootstyle=SUCCESS, 
            width=20
        )
        self.slice_button.pack(pady=20)
        
        # Zone de statut
        self.status_var = StringVar()
        status_label = Label(main_tab, textvariable=self.status_var, wraplength=600)
        status_label.pack(fill=X, pady=10)
        
        # ===== ONGLET CONFIGURATION =====
        
        settings_frame = Frame(settings_tab)
        settings_frame.pack(fill=BOTH, expand=YES)
        
        # Section apparence
        self.appearance_frame = LabelFrame(settings_frame, text=self.translations.get("appearance", "Appearance"), padding=10)
        self.appearance_frame.pack(fill=X, pady=10)
        
        # Langue
        lang_frame = Frame(self.appearance_frame)
        lang_frame.pack(fill=X, pady=5)
        self.lang_label = Label(lang_frame, text=self.translations.get("language", "Language:"))
        self.lang_label.pack(side=LEFT, padx=5)
        
        # Utiliser une Combobox pour la langue car il peut y avoir beaucoup de langues
        lang_combobox = Combobox(
            lang_frame, 
            textvariable=self.language, 
            values=list(self.available_languages.keys()),
            state="readonly", 
            width=20
        )
        lang_combobox.pack(side=LEFT, padx=5)
        
        # Thème
        theme_frame = Frame(self.appearance_frame)
        theme_frame.pack(fill=X, pady=5)
        self.theme_label = Label(theme_frame, text=self.translations.get("theme", "Theme:"))
        self.theme_label.pack(side=LEFT, padx=5)
        
        # Utiliser une Spinbox pour le thème
        theme_spinbox = Spinbox(
            theme_frame, 
            textvariable=self.theme, 
            values=self.available_themes,
            state="readonly", 
            width=20
        )
        theme_spinbox.pack(side=LEFT, padx=5)
        
        # Section À propos
        self.about_frame = LabelFrame(settings_frame, text=self.translations.get("about", "About"), padding=10)
        self.about_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Contenu À propos
        about_content = Frame(self.about_frame)
        about_content.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Titre de l'application
        app_title = Label(about_content, text="Text Slicer", font=("TkDefaultFont", 14, "bold"))
        app_title.pack(pady=5)
        
        # Version
        version_label = Label(about_content, text="Version 1.0")
        version_label.pack()
        
        # Description
        self.app_description = Label(
            about_content, 
            text=self.translations.get("app_description", "An application to split text files into multiple parts based on word count."),
            wraplength=500, 
            justify="center"
        )
        self.app_description.pack(pady=10)
        
        # Auteur
        self.author_label = Label(about_content, text=self.translations.get("created_by", "Created by Boris Hanicotte"))
        self.author_label.pack()
        
        # Séparateur
        Separator(about_content, orient=HORIZONTAL).pack(fill=X, pady=15)
        
        # Informations sur la traduction
        self.translation_info_title = Label(
            about_content, 
            text=self.translations.get("translation_info", "Translation Information"), 
            font=("TkDefaultFont", 11, "bold")
        )
        self.translation_info_title.pack(pady=5)
        
        # Frame pour les informations de traduction
        self.translation_info_frame = Frame(about_content)
        self.translation_info_frame.pack(fill=X, pady=5)
        
        # Note sur les traductions
        self.translation_note = Label(
            about_content, 
            text=self.translations.get("translation_note", "Select your preferred language from the menu above."),
            wraplength=500
        )
        self.translation_note.pack(pady=10)
        
        # Initialiser les informations de traduction
        self.update_translation_info()

    def update_translation_info(self):
        """Met à jour les informations sur la traduction actuelle"""
        # Supprimer les widgets existants
        for widget in self.translation_info_frame.winfo_children():
            widget.destroy()
        
        # Créer une grille pour les informations de traduction
        info_grid = Frame(self.translation_info_frame)
        info_grid.pack(fill=X, pady=5)
        
        # Ajouter les informations de traduction
        row = 0
        
        # Langue
        Label(info_grid, text=self.translations.get("translator", "Translator") + ":", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=W, padx=5, pady=2)
        Label(info_grid, text=self.current_language_metadata.get("author", "Unknown")).grid(row=row, column=1, sticky=W, padx=5, pady=2)
        row += 1
        
        # Version
        Label(info_grid, text=self.translations.get("version", "Version") + ":", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=W, padx=5, pady=2)
        Label(info_grid, text=self.current_language_metadata.get("version", "1.0")).grid(row=row, column=1, sticky=W, padx=5, pady=2)
        row += 1
        
        # Date de création
        Label(info_grid, text=self.translations.get("created", "Created on") + ":", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=W, padx=5, pady=2)
        Label(info_grid, text=self.current_language_metadata.get("created", "Unknown")).grid(row=row, column=1, sticky=W, padx=5, pady=2)
        row += 1
        
        # Commentaire
        if "comment" in self.current_language_metadata and self.current_language_metadata["comment"]:
            Label(info_grid, text=self.translations.get("comment", "Comment") + ":", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=W, padx=5, pady=2)
            comment_label = Label(info_grid, text=self.current_language_metadata.get("comment", ""), wraplength=350)
            comment_label.grid(row=row, column=1, sticky=W, padx=5, pady=2)
    
    def toggle_max_words(self):
        if self.cut_at_newline.get():
            self.max_entry.configure(state="disabled")
        else:
            self.max_entry.configure(state="normal")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title=self.translations.get("file_selection", "File Selection"),
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            self.input_file_path.set(file_path)
            # Enregistrer le dernier répertoire utilisé
            self.config["last_input_directory"] = os.path.dirname(file_path)
            self.save_config()
    
    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(
            title=self.translations.get("output_folder", "Output Folder"),
            initialdir=self.output_folder.get()
        )
        if folder_path:
            self.output_folder.set(folder_path)
            self.save_config()
    
    def clear_file_path(self):
        self.input_file_path.set("")
    
    def slice_text(self):
        input_file = self.input_file_path.get()
        output_folder = self.output_folder.get()
        
        if not input_file:
            self.status_var.set(self.translations.get("error_no_file", "Error: No file selected."))
            return
        
        if not os.path.exists(input_file):
            error_msg = self.translations.get("error_file_not_exist", "Error: The file {file} does not exist.")
            self.status_var.set(error_msg.format(file=input_file))
            return
        
        try:
            # Créer le dossier de sortie s'il n'existe pas
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Découper le fichier
            number_of_parts = self.split_text_into_files(
                input_file, 
                output_folder, 
                self.average_words.get(), 
                self.max_words.get() if not self.cut_at_newline.get() else None,
                self.preserve_newlines.get(),
                self.cut_at_newline.get()
            )
            
            success_msg = self.translations.get("success_message", "The text has been divided into {count} files in the folder '{folder}'.")
            self.status_var.set(success_msg.format(count=number_of_parts, folder=output_folder))
            
            # Sauvegarder les paramètres actuels
            self.save_config()
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def split_text_into_files(self, input_file, output_folder, average_words=500, max_words=1000, 
                              preserve_newlines=False, cut_at_newline=False):
        # Lire le contenu du fichier source
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read()

        chunks = []
        
        if preserve_newlines:
            # Préserver les retours à la ligne
            if cut_at_newline:
                # Diviser le texte en paragraphes (séparés par des sauts de ligne)
                paragraphs = re.split(r'\n\s*\n', text)
                current_chunk = []
                current_word_count = 0
                
                for paragraph in paragraphs:
                    paragraph_words = len(paragraph.split())
                    
                    if current_word_count + paragraph_words <= average_words:
                        current_chunk.append(paragraph)
                        current_word_count += paragraph_words
                    else:
                        # Ajouter le morceau actuel et commencer un nouveau
                        if current_chunk:
                            chunks.append("\n\n".join(current_chunk))
                        current_chunk = [paragraph]
                        current_word_count = paragraph_words
                
                # Ajouter le dernier morceau
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
            else:
                # Diviser en phrases tout en préservant les sauts de ligne
                lines = text.split('\n')
                current_chunk = []
                current_word_count = 0
                
                for line in lines:
                    sentences = re.split(r'(?<=[.!?])\s+', line)
                    for sentence in sentences:
                        if not sentence.strip():
                            continue
                        
                        word_count = len(sentence.split())
                        
                        if current_word_count + word_count <= max_words:
                            current_chunk.append(sentence)
                            current_word_count += word_count
                        elif current_word_count >= average_words:
                            chunks.append(" ".join(current_chunk))
                            current_chunk = [sentence]
                            current_word_count = word_count
                        else:
                            current_chunk.append(sentence)
                            current_word_count += word_count
                    
                    # Ajouter un saut de ligne après chaque ligne originale
                    if current_chunk:
                        current_chunk[-1] += "\n"
                
                # Ajouter le dernier morceau
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
        else:
            # Diviser le texte en phrases sans préserver les sauts de ligne
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = []
            current_word_count = 0
            
            for sentence in sentences:
                word_count = len(sentence.split())
                
                if cut_at_newline:
                    # Vérifier si on a atteint la moyenne de mots et s'il y a un saut de ligne
                    if current_word_count >= average_words and '\n' in sentence:
                        # Couper au prochain saut de ligne
                        parts = sentence.split('\n', 1)
                        current_chunk.append(parts[0])
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [parts[1]] if len(parts) > 1 else []
                        current_word_count = len(parts[1].split()) if len(parts) > 1 else 0
                    else:
                        current_chunk.append(sentence)
                        current_word_count += word_count
                else:
                    if current_word_count + word_count <= max_words:
                        current_chunk.append(sentence)
                        current_word_count += word_count
                    elif current_word_count >= average_words:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_word_count = word_count
                    else:
                        current_chunk.append(sentence)
                        current_word_count += word_count
            
            # Ajouter le dernier morceau
            if current_chunk:
                chunks.append(" ".join(current_chunk))

        # Enregistrer chaque morceau dans un fichier distinct
        prefix = self.file_prefix.get()
        for i, chunk in enumerate(chunks):
            file_name = f"{prefix}_{i+1:04d}.txt"
            output_path = os.path.join(output_folder, file_name)
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(chunk)

        return len(chunks)

if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")
    app = TextSlicerApp(root)
    root.mainloop()
