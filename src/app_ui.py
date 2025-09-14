
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os, sys, subprocess
import pandas as pd

from .config_loader import ConfigManager
from .file_io import DataLoader
from .app_logic import CalculationEngine, _kwh_totals

APP_VERSION = 'Chat149'

class AppGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"Répartition des Charges - Annuel ({APP_VERSION})")
        self.base_dir = Path(os.path.dirname(os.path.dirname(__file__))).resolve()
        (self.base_dir / "out").mkdir(exist_ok=True, parents=True)
        (self.base_dir / "assets").mkdir(exist_ok=True, parents=True)

        style = ttk.Style()
        try: style.theme_use('clam')
        except Exception: pass
        style.configure("TButton", padding=6)
        style.configure("Success.TLabel", foreground="#0a7f2e")
        style.configure("Warn.TLabel", foreground="#c25a00")
        style.configure("Info.TLabel", foreground="#1f4e79")

        self.config_mgr = ConfigManager(self.base_dir)
        self.loader = DataLoader(self.config_mgr)
        self.engine = CalculationEngine(self.config_mgr)

        self.details_df = pd.DataFrame()
        self.details_text = ""
        self.rep_df = pd.DataFrame()
        self.previews = {}
        self.tenants_df = pd.DataFrame()
        self.frais_df = pd.DataFrame()
        self.tree_frais = None
        self.tree_pac_energy = None

        import json
        defaults = {}
        pjson = (self.base_dir / "assets" / "UserSettings.json")
        if pjson.exists():
            try: defaults = json.loads(pjson.read_text(encoding="utf-8"))
            except Exception: defaults = {}
        self.var_charges_path = tk.StringVar(value=self.config_mgr.load_user_setting('charges_path', defaults.get("charges_path","")))
        self.var_tenants_path = tk.StringVar(value=self.config_mgr.load_user_setting('tenants_path', defaults.get("tenants_path","")))
        self.var_frais_path   = tk.StringVar(value=self.config_mgr.load_user_setting('frais_path', defaults.get("frais_path","")))
        self.var_si_path      = tk.StringVar(value=self.config_mgr.load_user_setting('si_path', defaults.get("si_path","")))
        self.var_output_dir   = tk.StringVar(value=self.config_mgr.load_user_setting('output_dir', str((self.base_dir/'out').resolve())))
        self.var_period       = tk.StringVar(value="2025-07")

        self.lbl_load_status = None
        self.lbl_prep_status = None

        self._build_tabs()

    def _make_tree(self, parent):
        tv = ttk.Treeview(parent, show="headings", height=16)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        tv.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        vsb.pack(side="right", fill="y")
        return tv

    def _fill_tree_df(self, tv: ttk.Treeview, df: pd.DataFrame):
        for c in tv.get_children(): tv.delete(c)
        if df is None or df.empty:
            tv["columns"] = ["(vide)"]; tv.heading("(vide)", text="(vide)"); tv.column("(vide)", width=200); return
        
        # Check if this is a grouped dataframe (has 'Groupe' column) and it's the frais tree
        if 'Groupe' in df.columns and tv == getattr(self, 'tree_frais', None):
            self._fill_tree_hierarchical(tv, df)
        else:
            self._fill_tree_flat(tv, df)
    
    def _fill_tree_flat(self, tv: ttk.Treeview, df: pd.DataFrame):
        """Fill tree with flat data (original behavior)"""
        cols = list(df.columns)
        tv["columns"] = cols
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=120, stretch=True)
        for _, row in df.iterrows():
            tv.insert("", "end", values=[row[c] for c in cols])
    
    def _fill_tree_hierarchical(self, tv: ttk.Treeview, df: pd.DataFrame):
        """Fill tree with hierarchical data grouped by 'Groupe' column"""
        cols = list(df.columns)
        tv["columns"] = cols
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=120, stretch=True)
        
        # Group data by 'Groupe' column
        grouped = df.groupby('Groupe', sort=False)
        
        for group_name, group_df in grouped:
            # Create parent node for the group
            group_node = tv.insert("", "end", values=[group_name] + [""] * (len(cols) - 1), open=True)
            
            # Add child rows for each item in the group
            for _, row in group_df.iterrows():
                tv.insert(group_node, "end", values=[row[c] for c in cols])

    def _build_tabs(self):
        self.nb = ttk.Notebook(self.root); self.nb.pack(fill="both", expand=True)
        self.tab_files = ttk.Frame(self.nb); self.nb.add(self.tab_files, text="Fichiers & Config")
        self.tab_preview = ttk.Frame(self.nb); self.nb.add(self.tab_preview, text="Aperçu données")
        self.tab_reps = ttk.Frame(self.nb); self.nb.add(self.tab_reps, text="Répartitions")
        self.tab_calc = ttk.Frame(self.nb); self.nb.add(self.tab_calc, text="Calculs & Détails")
        self.tab_outputs = ttk.Frame(self.nb); self.nb.add(self.tab_outputs, text="Sorties")

        frm = ttk.Frame(self.tab_files); frm.pack(fill="x", padx=10, pady=10)
        def row(lbl, var, is_dir=False):
            f = ttk.Frame(frm); f.pack(fill="x", pady=4)
            ttk.Label(f, text=lbl, width=30).pack(side="left")
            e = ttk.Entry(f, textvariable=var, width=95); e.pack(side="left", fill="x", expand=True)
            ttk.Button(f, text="Parcourir...", command=lambda:self._choose(var, is_dir)).pack(side="left", padx=6)
        row("Charges annuelles (Excel)", self.var_charges_path)
        row("Locataires (Excel)", self.var_tenants_path)
        row("Frais divers (Excel)", self.var_frais_path)
        row("Données SI (Excel)", self.var_si_path)
        row("Dossier de sortie", self.var_output_dir, is_dir=True)
        ttk.Label(frm, text="Période (AAAA-MM):").pack(side="left", padx=(2,4)); ttk.Entry(frm, textvariable=self.var_period, width=10).pack(side="left")

        vfrm = ttk.Frame(self.tab_files); vfrm.pack(fill="x", padx=10, pady=(0,6))
        ttk.Button(vfrm, text="Vérifier les chemins", command=self._verify_paths).pack(side="left")

        btns = ttk.Frame(self.tab_files); btns.pack(fill="x", padx=10, pady=6)
        ttk.Button(btns, text="Charger les données", command=self._load_all).pack(side="left")
        self.lbl_load_status = ttk.Label(btns, text="", style="Success.TLabel"); self.lbl_load_status.pack(side="left", padx=10)
        ttk.Button(btns, text="Préparer Répartition", command=self._prepare).pack(side="left", padx=(20,0))
        self.lbl_prep_status = ttk.Label(btns, text="", style="Success.TLabel"); self.lbl_prep_status.pack(side="left", padx=10)

        # preview tab
        self.preview_nb = ttk.Notebook(self.tab_preview); self.preview_nb.pack(fill="both", expand=True)
        self.trees = {}
        btnf = ttk.Frame(self.tab_preview); btnf.pack(fill="x")
        ttk.Button(btnf, text="Enregistrer Frais divers", command=self._save_frais).pack(side="right", padx=8, pady=6)

        # reps tab
        self.tree_reps = self._make_tree(self.tab_reps)

        # calc & details tab
        frm_calc = ttk.Frame(self.tab_calc); frm_calc.pack(fill="both", expand=True)
        left = ttk.Frame(frm_calc); right = ttk.Frame(frm_calc)
        left.pack(side="left", fill="both", expand=True); right.pack(side="left", fill="both", expand=True)
        self.tree_price = self._make_tree(left)
        ttk.Label(right, text="Détail explicatif", style="Info.TLabel").pack(anchor="w", padx=6, pady=(8,0))
        self.txt_details = tk.Text(right, height=24); self.txt_details.pack(fill="both", expand=True, padx=6, pady=6)

        # outputs tab
        cmd = ttk.Frame(self.tab_outputs); cmd.pack(fill="x", pady=6)
        ttk.Button(cmd, text="Exporter log Excel", command=self._export_log).pack(side="left", padx=4)
        ttk.Button(cmd, text="Générer factures (XLSX)", command=self._export_invoices).pack(side="left", padx=4)
        ttk.Button(cmd, text="Générer factures (PDF)", command=self._export_invoices_pdf).pack(side="left", padx=4)
        ttk.Button(cmd, text="Rafraîchir la liste", command=self._refresh_files).pack(side="left", padx=4)
        self.tree_files = self._make_tree(self.tab_outputs)
        self.tree_files.bind("<Double-1>", self._open_selected_file)

    def _verify_paths(self):
        missing = []
        pairs = [
            ("Charges annuelles", self.var_charges_path),
            ("Locataires", self.var_tenants_path),
            ("Frais divers", self.var_frais_path),
            ("Données SI", self.var_si_path),
        ]
        for label, var in pairs:
            val = self.config_mgr.resolve_path(var.get())
            if val != var.get(): var.set(val)
            if val and not Path(val).exists():
                missing.append(f"- {label}: {val}")
        if missing:
            messagebox.showerror("Chemins introuvables", "Les fichiers suivants sont introuvables:\n\n" + "\n".join(missing) + "\n\nVeuillez corriger les chemins dans 'Fichiers & Config'.")
        else:
            messagebox.showinfo("Vérification", "Tous les chemins configurés existent.")

    def _choose(self, var, is_dir=False):
        if is_dir:
            p = filedialog.askdirectory(initialdir=self.base_dir)
        else:
            p = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx;*.xls")], initialdir=self.base_dir)
        if p:
            var.set(p)
            key = 'charges_path' if var is self.var_charges_path else ('tenants_path' if var is self.var_tenants_path else ('frais_path' if var is self.var_frais_path else ('si_path' if var is self.var_si_path else ('output_dir' if var is self.var_output_dir else None))))
            if key: self.config_mgr.save_user_setting(key, p)

    def _load_all(self):
        try:
            charges = Path(self.config_mgr.resolve_path(self.var_charges_path.get()))
            tenants = Path(self.config_mgr.resolve_path(self.var_tenants_path.get())) if self.var_tenants_path.get() else None
            if not charges.exists():
                raise FileNotFoundError(f"Charges annuelles introuvable: {charges}")
            previews, tenants_df = self.engine.preview_tables(charges, tenants)
            self.previews = previews; self.tenants_df = tenants_df if tenants_df is not None else pd.DataFrame()
            for child in self.preview_nb.winfo_children(): child.destroy()
            self.trees = {}
            for sh, df in previews.items():
                tab = ttk.Frame(self.preview_nb); self.preview_nb.add(tab, text=sh)
                tv = self._make_tree(tab); self.trees[sh] = tv
                self._fill_tree_df(tv, df)
            # Frais divers
            if self.var_frais_path.get():
                try:
                    xlsf = pd.ExcelFile(self.config_mgr.resolve_path(self.var_frais_path.get()))
                    shname = xlsf.sheet_names[0]
                    self.frais_sheet_name = shname
                    self.frais_df = xlsf.parse(shname)
                    tabf = ttk.Frame(self.preview_nb); self.preview_nb.add(tabf, text="Frais divers")
                    self.tree_frais = self._make_tree(tabf)
                    self._fill_tree_df(self.tree_frais, self.frais_df)
                    self.tree_frais.bind("<Double-1>", lambda ev: self._start_edit_cell(ev, self.tree_frais, 'frais'))
                    self.tree_frais.bind("<Button-3>", lambda ev: self._show_frais_context_menu(ev))  # Right-click context menu
                except Exception:
                    pass
            # Locataires
            if self.tenants_df is not None and not self.tenants_df.empty:
                tab = ttk.Frame(self.preview_nb); self.preview_nb.add(tab, text="Locataires")
                tv = self._make_tree(tab); self.trees["Locataires"]=tv; self._fill_tree_df(tv, self.tenants_df)
            # Synthèse PAC/Energie
            try:
                from .app_logic import _kwh_totals
                xls = pd.ExcelFile(charges)
                hp_p,hc_p,sol_p = _kwh_totals(xls, "PAC")
                hp_c,hc_c,sol_c = _kwh_totals(xls, "Communs")
                ef = 0.0; ec = 0.0
                if "Eau Froide" in xls.sheet_names: ef = float(pd.to_numeric(xls.parse("Eau Froide").iloc[-1].drop(labels=["Période"], errors="ignore"), errors="coerce").fillna(0).sum())
                if "Eau Chaude" in xls.sheet_names: ec = float(pd.to_numeric(xls.parse("Eau Chaude").iloc[-1].drop(labels=["Période"], errors="ignore"), errors="coerce").fillna(0).sum())
                df_sum = pd.DataFrame([
                    {"Bloc":"PAC","HP_kWh":hp_p,"HC_kWh":hc_p,"Sol_kWh":sol_p},
                    {"Bloc":"Communs","HP_kWh":hp_c,"HC_kWh":hc_c,"Sol_kWh":sol_c},
                    {"Bloc":"Eau (m³)","EF_m3":ef,"EC_m3":ec}
                ])
                tab = ttk.Frame(self.preview_nb); self.preview_nb.add(tab, text="PAC/Energie")
                self.tree_pac_energy = self._make_tree(tab); self._fill_tree_df(self.tree_pac_energy, df_sum)
            except Exception:
                pass
            sheets = len(previews)
            apts = len(self.tenants_df) if self.tenants_df is not None else 0
            self.lbl_load_status.configure(text=f"✓ Chargé — Feuilles: {sheets} | Appartements: {apts}")
        except Exception as e:
            self.lbl_load_status.configure(text="Erreur")
            messagebox.showerror("Erreur chargement", f"{e}\n\nVérifiez les chemins dans l’onglet Fichiers & Config (ou cliquez ‘Vérifier les chemins’).")

    def _start_edit_cell(self, event, tv, df_name):
        region = tv.identify('region', event.x, event.y); 
        if region != 'cell': return
        col_id = tv.identify_column(event.x); row_id = tv.identify_row(event.y)
        if not row_id or not col_id: return
        
        # Don't allow editing of group header rows (parent nodes)
        if tv.parent(row_id) == "":  # This is a parent/group node
            if df_name == 'frais' and hasattr(self, 'frais_df') and 'Groupe' in getattr(self, 'frais_df', pd.DataFrame()).columns:
                return  # Skip editing group headers
        
        col_index = int(col_id.replace('#','')) - 1
        x,y,w,h = tv.bbox(row_id, col_id); value = tv.set(row_id, tv['columns'][col_index])
        self._edit_entry = tk.Entry(tv); self._edit_entry.insert(0, value)
        self._edit_entry.place(x=x, y=y, width=w, height=h); self._edit_entry.focus_set()
        self._edit_entry.bind("<Return>", lambda e: self._commit_edit(tv, row_id, col_index, df_name))
        self._edit_entry.bind("<FocusOut>", lambda e: self._commit_edit(tv, row_id, col_index, df_name))

    def _commit_edit(self, tv, row_id, col_index, df_name):
        new_val = self._edit_entry.get() if hasattr(self, "_edit_entry") else None
        if hasattr(self, "_edit_entry"): self._edit_entry.destroy(); delattr(self, "_edit_entry")
        if new_val is None: return
        cols = list(tv['columns']); row_vals = list(tv.item(row_id, 'values')); row_vals[col_index] = new_val
        tv.item(row_id, values=row_vals)
        if df_name == 'frais' and isinstance(self.frais_df, pd.DataFrame) and not self.frais_df.empty:
            try:
                # Handle hierarchical editing
                if 'Groupe' in self.frais_df.columns and tv == getattr(self, 'tree_frais', None):
                    self._update_frais_df_hierarchical(tv, row_id, col_index, new_val)
                else:
                    # Original flat editing
                    r_index = tv.index(row_id); col_name = cols[col_index]
                    self.frais_df.at[self.frais_df.index[r_index], col_name] = new_val
            except Exception: pass
    
    def _update_frais_df_hierarchical(self, tv, row_id, col_index, new_val):
        """Update DataFrame when editing in hierarchical mode"""
        try:
            cols = list(tv['columns'])
            col_name = cols[col_index]
            row_values = tv.item(row_id, 'values')
            
            # Find the corresponding row in the DataFrame
            # For hierarchical display, we need to match on all column values
            groupe_value = row_values[0] if len(row_values) > 0 else ""
            
            # If it's a child row (has a parent), get all the row values to match
            if tv.parent(row_id) != "":  # This is a child row
                # Find the matching row in the DataFrame
                for idx, df_row in self.frais_df.iterrows():
                    # Match all values except the one being edited
                    if all(str(df_row[cols[i]]) == str(row_values[i]) for i in range(len(cols)) if i != col_index):
                        self.frais_df.at[idx, col_name] = new_val
                        break
        except Exception as e:
            print(f"Error updating DataFrame in hierarchical mode: {e}")

    def _save_frais(self):
        try:
            path = Path(self.config_mgr.resolve_path(self.var_frais_path.get()))
            if not path.exists(): raise FileNotFoundError(f"Fichier Frais divers introuvable: {path}")
            with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='replace') as wr:
                sheet_name = getattr(self, 'frais_sheet_name', None)
                if not sheet_name:
                    try:
                        xls = pd.ExcelFile(path); sheet_name = xls.sheet_names[0]
                    except Exception:
                        sheet_name = "Frais divers"
                self.frais_df.to_excel(wr, index=False, sheet_name=sheet_name)
            messagebox.showinfo("Sauvegarde", "Frais divers enregistrés.")
        except Exception as e:
            messagebox.showerror("Erreur sauvegarde Frais", str(e))

    def _prepare(self):
        try:
            charges = Path(self.config_mgr.resolve_path(self.var_charges_path.get()))
            if not charges.exists():
                raise FileNotFoundError(f"Charges annuelles introuvable: {charges}")
            tenants_df = self.tenants_df if not self.tenants_df.empty else pd.DataFrame()
            rep, details, details_text = self.engine.build_repartitions(charges, tenants_df)
            self.rep_df = rep; self.details_df = details; self.details_text = details_text
            self._fill_tree_df(self.tree_reps, rep)
            self._fill_tree_df(self.tree_price, details)
            self.txt_details.delete("1.0","end"); self.txt_details.insert("end", details_text)
            rows = len(rep) if rep is not None else 0
            self.lbl_prep_status.configure(text=f"✓ Répartition prête — lignes: {rows}")
        except Exception as e:
            self.lbl_prep_status.configure(text="Erreur")
            messagebox.showerror("Erreur préparation", f"{e}\n\nAssurez-vous que Charges/Locataires existent (utilisez ‘Vérifier les chemins’).")

    def _export_log(self):
        try:
            fp = self.engine.export_log(Path(self.var_output_dir.get()), self.var_period.get(), self.rep_df)
            messagebox.showinfo("Log exporté", f"Historique mis à jour :\n{fp}")
            self._refresh_files()
        except Exception as e:
            messagebox.showerror("Erreur export log", str(e))

    def _export_invoices(self):
        try:
            base, files = self.engine.export_invoices_xlsx(Path(self.var_output_dir.get()), self.var_period.get(), self.rep_df, self.tenants_df)
            messagebox.showinfo("Factures", f"XLSX créés dans :\n{base}")
            self._refresh_files()
        except Exception as e:
            messagebox.showerror("Erreur factures", str(e))

    def _export_invoices_pdf(self):
        try:
            base, files = self.engine.export_invoices_pdf(Path(self.var_output_dir.get()), self.var_period.get(), self.rep_df, self.tenants_df)
            messagebox.showinfo("Factures PDF", f"PDF créés dans :\n{base}")
            self._refresh_files()
        except Exception as e:
            messagebox.showerror("Erreur factures PDF", str(e))

    def _refresh_files(self):
        outdir = Path(self.var_output_dir.get())
        rows = []
        if outdir.exists():
            for root, _, files in os.walk(outdir):
                for f in files:
                    full = Path(root)/f
                    rows.append({"Nom": f, "Dossier": str(Path(root)), "Chemin": str(full)})
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Nom","Dossier","Chemin"])
        self._fill_tree_df(self.tree_files, df)

    def _open_selected_file(self, event):
        cur = self.tree_files.focus()
        if not cur: return
        vals = self.tree_files.item(cur, "values")
        if not vals: return
        fp = vals[-1]
        try:
            if sys.platform.startswith("win"):
                os.startfile(fp)  # type: ignore
            elif sys.platform == "darwin":
                subprocess.Popen(["open", fp])
            else:
                subprocess.Popen(["xdg-open", fp])
        except Exception as e:
            messagebox.showerror("Ouverture de fichier", str(e))

    def _show_frais_context_menu(self, event):
        """Show context menu for Frais divers tree operations"""
        try:
            from tkinter import Menu
            # Get the item at the cursor position
            item_id = self.tree_frais.identify_row(event.y)
            
            # Create context menu
            context_menu = Menu(self.root, tearoff=0)
            
            if item_id:
                # If an item is selected
                self.tree_frais.selection_set(item_id)
                
                # Check if it's a group header or data row
                is_group_header = self.tree_frais.parent(item_id) == ""
                
                if is_group_header:
                    context_menu.add_command(label="Ajouter un élément à ce groupe", 
                                           command=lambda: self._add_frais_item(item_id))
                else:
                    context_menu.add_command(label="Modifier", 
                                           command=lambda: self._edit_frais_item(item_id))
                    context_menu.add_command(label="Supprimer", 
                                           command=lambda: self._delete_frais_item(item_id))
            else:
                # If no item selected, show general options
                context_menu.add_command(label="Ajouter un nouvel élément", 
                                       command=self._add_frais_item_dialog)
            
            # Show menu at cursor position
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")
    
    def _add_frais_item(self, parent_group_id=None):
        """Add a new item to a specific group"""
        try:
            if not hasattr(self, 'frais_df') or self.frais_df.empty:
                messagebox.showwarning("Ajouter élément", "Aucune donnée Frais divers chargée")
                return
            
            # Get the group name from parent
            if parent_group_id:
                group_values = self.tree_frais.item(parent_group_id, 'values')
                group_name = group_values[0] if group_values else ""
            else:
                group_name = ""
            
            self._show_add_frais_dialog(group_name)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {e}")
    
    def _add_frais_item_dialog(self):
        """Show dialog to add a new frais item"""
        self._show_add_frais_dialog()
    
    def _show_add_frais_dialog(self, default_group=""):
        """Show dialog to add a new frais item"""
        try:
            from tkinter import simpledialog, Toplevel, Label, Entry, Button, StringVar, OptionMenu
            
            # Create dialog window
            dialog = Toplevel(self.root)
            dialog.title("Ajouter un élément")
            dialog.geometry("400x200")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"400x200+{x}+{y}")
            
            # Variables
            desc_var = StringVar()
            montant_var = StringVar(value="0")
            groupe_var = StringVar(value=default_group)
            
            # Get available groups
            if 'Groupe' in self.frais_df.columns:
                groups = self.frais_df['Groupe'].unique().tolist()
            else:
                groups = [""]
            
            # UI elements
            Label(dialog, text="Description:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
            desc_entry = Entry(dialog, textvariable=desc_var, width=40)
            desc_entry.grid(row=0, column=1, padx=10, pady=5)
            
            Label(dialog, text="Montant (CHF):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            montant_entry = Entry(dialog, textvariable=montant_var, width=40)
            montant_entry.grid(row=1, column=1, padx=10, pady=5)
            
            Label(dialog, text="Groupe:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
            if groups and groups != [""]:
                groupe_menu = OptionMenu(dialog, groupe_var, *groups)
                groupe_menu.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
            else:
                groupe_entry = Entry(dialog, textvariable=groupe_var, width=40)
                groupe_entry.grid(row=2, column=1, padx=10, pady=5)
            
            # Buttons
            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
            
            def on_ok():
                desc = desc_var.get().strip()
                groupe = groupe_var.get().strip()
                try:
                    montant = float(montant_var.get())
                except ValueError:
                    montant = 0.0
                
                if not desc:
                    messagebox.showwarning("Validation", "La description est requise")
                    return
                
                if not groupe:
                    messagebox.showwarning("Validation", "Le groupe est requis")
                    return
                
                # Add to DataFrame
                new_row = pd.DataFrame([{
                    'Description': desc,
                    'Montant (CHF)': montant,
                    'Groupe': groupe
                }])
                self.frais_df = pd.concat([self.frais_df, new_row], ignore_index=True)
                
                # Refresh display
                self._fill_tree_df(self.tree_frais, self.frais_df)
                dialog.destroy()
            
            def on_cancel():
                dialog.destroy()
            
            Button(btn_frame, text="OK", command=on_ok).pack(side="left", padx=5)
            Button(btn_frame, text="Annuler", command=on_cancel).pack(side="left", padx=5)
            
            # Focus on description field
            desc_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du dialogue: {e}")
    
    def _edit_frais_item(self, item_id):
        """Edit the selected frais item"""
        # This functionality already exists via double-click
        # We can trigger it programmatically or just show a message
        messagebox.showinfo("Modifier", "Double-cliquez sur une cellule pour la modifier")
    
    def _delete_frais_item(self, item_id):
        """Delete the selected frais item"""
        try:
            if not hasattr(self, 'frais_df') or self.frais_df.empty:
                return
            
            # Confirm deletion
            result = messagebox.askyesno("Confirmer suppression", 
                                       "Êtes-vous sûr de vouloir supprimer cet élément?")
            if not result:
                return
            
            # Get row values to identify the row in DataFrame
            row_values = self.tree_frais.item(item_id, 'values')
            if not row_values:
                return
            
            # Find matching row in DataFrame
            cols = list(self.tree_frais['columns'])
            for idx, df_row in self.frais_df.iterrows():
                if all(str(df_row[cols[i]]) == str(row_values[i]) for i in range(len(cols))):
                    # Remove from DataFrame
                    self.frais_df = self.frais_df.drop(idx).reset_index(drop=True)
                    break
            
            # Refresh display
            self._fill_tree_df(self.tree_frais, self.frais_df)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
