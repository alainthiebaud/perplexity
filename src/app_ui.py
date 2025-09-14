import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import pandas as pd
import threading
import os
from src.config_loader import ConfigManager
from src.app_logic import CalculationEngine
from src.file_io import DataLoader

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat149 - Gestion Charges Appartements")
        self.master.geometry("900x700")
        
        # Initialize components
        self.config = ConfigManager(Path.cwd())
        self.engine = CalculationEngine(self.config)
        self.loader = DataLoader(self.config)
        
        # Data storage
        self.current_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Principal")
        
        # Config tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Fichiers & Config")
        
        # Output tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Sorties")
        
        self.setup_main_tab(main_frame)
        self.setup_config_tab(config_frame)
        self.setup_output_tab(output_frame)
        
    def setup_main_tab(self, parent):
        # Title
        title_label = ttk.Label(parent, text="Traitement des Charges", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main action button (merged functionality)
        main_button_frame = ttk.Frame(parent)
        main_button_frame.pack(pady=20)
        
        self.main_action_btn = ttk.Button(
            main_button_frame, 
            text="Charger les données et Préparer Répartition", 
            command=self.execute_main_action,
            style="Accent.TButton"
        )
        self.main_action_btn.pack(pady=10)
        
        # Progress display
        self.progress_var = tk.StringVar()
        self.progress_var.set("Prêt")
        progress_label = ttk.Label(parent, textvariable=self.progress_var, font=("Arial", 10))
        progress_label.pack(pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(parent, mode='indeterminate')
        self.progress_bar.pack(fill="x", padx=50, pady=5)
        
        # Results display frame
        results_frame = ttk.LabelFrame(parent, text="Résultats")
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview for displaying results
        self.results_tree = ttk.Treeview(results_frame, columns=("Appartement", "Chauffage_kWh", "Refroid_kWh", "Eau_froide_m3", "Eau_chaude_m3", "Montant_eau", "Montant_energie", "Total_CHF"), show="headings")
        
        # Configure columns
        columns = [
            ("Appartement", 100),
            ("Chauffage_kWh", 90),
            ("Refroid_kWh", 90),
            ("Eau_froide_m3", 90),
            ("Eau_chaude_m3", 90),
            ("Montant_eau", 90),
            ("Montant_energie", 90),
            ("Total_CHF", 90)
        ]
        
        for col, width in columns:
            self.results_tree.heading(col, text=col.replace("_", " "))
            self.results_tree.column(col, width=width)
        
        scrollbar_results = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar_results.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar_results.pack(side="right", fill="y")
        
    def setup_config_tab(self, parent):
        # Path configuration
        ttk.Label(parent, text="Configuration des chemins", font=("Arial", 14, "bold")).pack(pady=10)
        
        paths = [
            ("charges_path", "Fichier Charges annuelles"),
            ("tenants_path", "Fichier Locataires"),
            ("si_path", "Fichier Données SI"),
            ("output_dir", "Dossier de sortie")
        ]
        
        self.path_vars = {}
        
        for key, label in paths:
            frame = ttk.Frame(parent)
            frame.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(frame, text=f"{label}:", width=20).pack(side="left")
            
            var = tk.StringVar()
            var.set(self.config.load_user_setting(key, ""))
            self.path_vars[key] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=60)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            
            def browse_path(k=key):
                if k == "output_dir":
                    path = filedialog.askdirectory(title=f"Sélectionner {label}")
                else:
                    path = filedialog.askopenfilename(
                        title=f"Sélectionner {label}",
                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                    )
                if path:
                    self.path_vars[k].set(path)
                    self.config.save_user_setting(k, path)
            
            ttk.Button(frame, text="...", command=browse_path, width=3).pack(side="right")
        
        # Verify paths button
        verify_btn = ttk.Button(parent, text="Vérifier les chemins", command=self.verify_paths)
        verify_btn.pack(pady=20)
        
    def setup_output_tab(self, parent):
        ttk.Label(parent, text="Génération des factures", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Export buttons
        export_frame = ttk.Frame(parent)
        export_frame.pack(pady=20)
        
        self.export_xlsx_btn = ttk.Button(export_frame, text="Générer Factures XLSX", command=self.export_xlsx, state="disabled")
        self.export_xlsx_btn.pack(side="left", padx=10)
        
        self.export_pdf_btn = ttk.Button(export_frame, text="Générer Factures PDF", command=self.export_pdf, state="disabled")
        self.export_pdf_btn.pack(side="left", padx=10)
        
        # Refresh button
        refresh_btn = ttk.Button(parent, text="Rafraîchir la liste", command=self.refresh_output_list)
        refresh_btn.pack(pady=10)
        
        # Output files list
        list_frame = ttk.LabelFrame(parent, text="Fichiers générés")
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.output_tree = ttk.Treeview(list_frame, columns=("Nom", "Type", "Taille"), show="headings")
        self.output_tree.heading("Nom", text="Nom du fichier")
        self.output_tree.heading("Type", text="Type")
        self.output_tree.heading("Taille", text="Taille")
        
        self.output_tree.bind("<Double-1>", self.open_output_file)
        
        scrollbar_output = ttk.Scrollbar(list_frame, orient="vertical", command=self.output_tree.yview)
        self.output_tree.configure(yscrollcommand=scrollbar_output.set)
        
        self.output_tree.pack(side="left", fill="both", expand=True)
        scrollbar_output.pack(side="right", fill="y")
        
    def execute_main_action(self):
        """Main action that loads data and prepares distribution in one click"""
        self.main_action_btn.config(state="disabled")
        self.progress_bar.start()
        self.progress_var.set("Chargement en cours...")
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._execute_main_action_thread)
        thread.daemon = True
        thread.start()
        
    def _execute_main_action_thread(self):
        try:
            # Step 1: Verify paths
            self.progress_var.set("Vérification des chemins...")
            paths_ok = self.verify_paths(show_messages=False)
            if not paths_ok:
                self.progress_var.set("Erreur: Chemins invalides")
                return
            
            # Step 2: Load data
            self.progress_var.set("Chargement des données...")
            charges_path = Path(self.config.resolve_path(self.config.load_user_setting("charges_path", "")))
            tenants_path = Path(self.config.resolve_path(self.config.load_user_setting("tenants_path", "")))
            
            if not charges_path.exists():
                self.progress_var.set("Erreur: Fichier charges introuvable")
                return
                
            # Step 3: Preview and build calculations
            self.progress_var.set("Traitement des calculs...")
            previews, tenants_df = self.engine.preview_tables(charges_path, tenants_path)
            rep_df, details_df, details_text = self.engine.build_repartitions(charges_path, tenants_df)
            
            # Store results
            self.current_data = {
                'rep_df': rep_df,
                'details_df': details_df,
                'details_text': details_text,
                'tenants_df': tenants_df
            }
            
            # Step 4: Update UI
            self.master.after(0, self._update_results_display, rep_df)
            self.master.after(0, lambda: self.progress_var.set("Traitement terminé"))
            self.master.after(0, self._enable_export_buttons)
            
        except Exception as e:
            self.master.after(0, lambda: self.progress_var.set(f"Erreur: {str(e)}"))
            self.master.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors du traitement: {str(e)}"))
        finally:
            self.master.after(0, self.progress_bar.stop)
            self.master.after(0, lambda: self.main_action_btn.config(state="normal"))
    
    def _update_results_display(self, rep_df):
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add new items
        if rep_df is not None and not rep_df.empty:
            for _, row in rep_df.iterrows():
                values = [
                    row.get("Appartement", ""),
                    f"{row.get('Chauffage_kWh', 0):.2f}",
                    f"{row.get('Refroid_kWh', 0):.2f}",
                    f"{row.get('Eau_froide_m3', 0):.2f}",
                    f"{row.get('Eau_chaude_m3', 0):.2f}",
                    f"{row.get('Montant_eau', 0):.2f}",
                    f"{row.get('Montant_energie', 0):.2f}",
                    f"{row.get('Total_CHF', 0):.2f}"
                ]
                self.results_tree.insert("", "end", values=values)
    
    def _enable_export_buttons(self):
        self.export_xlsx_btn.config(state="normal")
        self.export_pdf_btn.config(state="normal")
    
    def verify_paths(self, show_messages=True):
        """Verify that all configured paths exist"""
        paths = ["charges_path", "tenants_path", "si_path"]
        missing = []
        
        for path_key in paths:
            path_str = self.config.load_user_setting(path_key, "")
            if not path_str:
                missing.append(f"{path_key}: Non configuré")
                continue
                
            resolved_path = self.config.resolve_path(path_str)
            if not Path(resolved_path).exists():
                missing.append(f"{path_key}: {resolved_path}")
        
        # Check output directory
        output_dir = self.config.load_user_setting("output_dir", "")
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        if missing and show_messages:
            messagebox.showwarning("Chemins manquants", 
                                 f"Les chemins suivants sont manquants ou invalides:\n" + 
                                 "\n".join(missing))
            return False
        elif not missing and show_messages:
            messagebox.showinfo("Vérification", "Tous les chemins sont valides!")
            
        return len(missing) == 0
    
    def export_xlsx(self):
        """Export invoices as Excel files"""
        if not self.current_data:
            messagebox.showwarning("Avertissement", "Aucune donnée à exporter. Effectuez d'abord le traitement principal.")
            return
            
        try:
            output_dir = Path(self.config.load_user_setting("output_dir", ""))
            period_label = "2025"  # Fixed period since date fields are removed
            
            _, files = self.engine.export_invoices_xlsx(
                output_dir, 
                period_label, 
                self.current_data['rep_df'], 
                self.current_data['tenants_df']
            )
            
            messagebox.showinfo("Export terminé", f"Factures XLSX générées:\n{len(files)} fichiers créés")
            self.refresh_output_list()
            
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur lors de l'export XLSX: {str(e)}")
    
    def export_pdf(self):
        """Export invoices as PDF files"""
        if not self.current_data:
            messagebox.showwarning("Avertissement", "Aucune donnée à exporter. Effectuez d'abord le traitement principal.")
            return
            
        try:
            output_dir = Path(self.config.load_user_setting("output_dir", ""))
            period_label = "2025"  # Fixed period since date fields are removed
            
            _, files = self.engine.export_invoices_pdf(
                output_dir, 
                period_label, 
                self.current_data['rep_df'], 
                self.current_data['tenants_df']
            )
            
            messagebox.showinfo("Export terminé", f"Factures PDF générées:\n{len(files)} fichiers créés")
            self.refresh_output_list()
            
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur lors de l'export PDF: {str(e)}")
    
    def refresh_output_list(self):
        """Refresh the list of output files"""
        # Clear existing items
        for item in self.output_tree.get_children():
            self.output_tree.delete(item)
        
        output_dir = self.config.load_user_setting("output_dir", "")
        if not output_dir or not Path(output_dir).exists():
            return
            
        output_path = Path(output_dir)
        
        # List files in output directory
        for file_path in output_path.rglob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                    file_type = file_path.suffix.upper() or "Fichier"
                    
                    self.output_tree.insert("", "end", values=(
                        file_path.name,
                        file_type,
                        size_str
                    ), tags=(str(file_path),))
                except Exception:
                    pass
    
    def open_output_file(self, event):
        """Open selected output file"""
        selection = self.output_tree.selection()
        if not selection:
            return
            
        item = self.output_tree.item(selection[0])
        if not item['tags']:
            return
            
        file_path = item['tags'][0]
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # macOS and Linux
                os.system(f'open "{file_path}"' if os.name == 'posix' else f'xdg-open "{file_path}"')
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")