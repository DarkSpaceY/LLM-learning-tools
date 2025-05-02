import json
import os
from typing import Dict, Any


class SettingsManager:
    def __init__(self, settings_dir: str = "settings"):
        self.settings_dir = settings_dir
        self.global_settings_file = os.path.join(
            settings_dir,
            "global_settings.json"
        )
        self.user_settings_file = os.path.join(
            settings_dir,
            "user_settings.json"
        )
        self.default_settings = {
            "default_provider": "openai",
            "theme": "light",
            "language": "zh-CN"
        }
        
        # 确保设置目录存在
        os.makedirs(settings_dir, exist_ok=True)
        
        # 初始化设置文件
        if not os.path.exists(self.user_settings_file):
            self.save_user_settings({
                "global": self.default_settings
            })

    def load_global_settings(self) -> Dict[str, Any]:
        """加载全局设置"""
        try:
            with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("global", self.default_settings)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_settings.copy()

    def save_global_settings(self, settings: Dict[str, Any]) -> None:
        """保存全局设置"""
        current_settings = self.load_user_settings({})
        current_settings["global"] = settings
        self.save_user_settings(current_settings)

    def load_user_settings(
        self,
        default: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """加载所有用户设置"""
        try:
            with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default if default is not None else {}

    def save_user_settings(self, settings: Dict[str, Any]) -> None:
        """保存用户设置"""
        os.makedirs(self.settings_dir, exist_ok=True)
        with open(self.user_settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def update_settings(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新用户设置"""
        all_settings = self.load_user_settings({})
        
        # 如果是全局设置，确保包含所有必要的字段
        if user_id == "global":
            current = all_settings.get(
                "global",
                self.default_settings.copy()
            )
            current.update(preferences)
            all_settings["global"] = current
        else:
            # 用户特定设置
            if user_id not in all_settings:
                all_settings[user_id] = {}
            all_settings[user_id].update(preferences)
        
        self.save_user_settings(all_settings)
        return all_settings[user_id]

    def get_merged_settings(self, user_id: str) -> Dict[str, Any]:
        """获取合并后的设置（全局设置 + 用户设置）"""
        all_settings = self.load_user_settings({})
        global_settings = all_settings.get(
            "global",
            self.default_settings.copy()
        )
        
        if user_id == "global":
            return global_settings
            
        user_settings = all_settings.get(user_id, {})
        # 合并设置，用户设置优先级更高
        merged = {**global_settings, **user_settings}
        return merged


# 创建设置管理器实例
settings_manager = SettingsManager()