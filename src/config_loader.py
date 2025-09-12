from pathlib import Path
import json

class ConfigManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir = self.base_dir / "assets"; self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.paths_json = self.assets_dir / "paths.json"
        self.usersettings_json = self.assets_dir / "UserSettings.json"
        self.legacy_json = self.base_dir / "user_settings.json"
        for p in (self.paths_json, self.usersettings_json, self.legacy_json):
            if not p.exists():
                p.write_text("{}", encoding="utf-8")

    def _load_json(self, p: Path):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _load_all(self):
        data = {}
        data.update(self._load_json(self.legacy_json))
        data.update(self._load_json(self.paths_json))
        data.update(self._load_json(self.usersettings_json))
        return data

    def load_user_setting(self, key: str, default=None):
        return self._load_all().get(key, default)

    def save_user_setting(self, key: str, value):
        allv = self._load_all(); allv[key] = value
        filtered = {k: allv.get(k,"") for k in ["charges_path","tenants_path","frais_path","si_path","output_dir"]}
        self.paths_json.write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8")
        self.usersettings_json.write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8")
        legacy = self._load_json(self.legacy_json); legacy[key] = value
        self.legacy_json.write_text(json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8")

    def resolve_path(self, p: str) -> str:
        """
        Normalise en évitant les problèmes d'échappement:
        - Convertit d'abord les backslashes en slashes pour manipuler
        - Tente la variante sans '.IS' dans C:/Users
        - Essaie versions en backslashes et slashes
        - Retourne le premier chemin existant, sinon une version backslash du chemin normalisé
        """
        if not p:
            return ""
        s = str(p)
        s_norm = s.replace("\\", "/")
        candidates = [s_norm]
        if "C:/Users/a.thiebaud.IS" in s_norm:
            candidates.append(s_norm.replace("C:/Users/a.thiebaud.IS", "C:/Users/a.thiebaud"))
        # backslash variants
        for c in list(candidates):
            candidates.append(c.replace("/", "\\"))
            candidates.append(c.replace("/", "\\"))
        for c in candidates:
            try:
                if Path(c).exists():
                    return c
            except Exception:
                pass
        return s_norm.replace("/", "\\")
