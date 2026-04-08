import tkinter as tk
from tkinter import messagebox
import winreg

EXPLORER_POLICIES = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
ZONE_MAP_DOMAINS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains"


def _open_or_create(root, path):
    return winreg.CreateKeyEx(root, path, 0, winreg.KEY_ALL_ACCESS)


def block_program(exe_name: str) -> None:
    """Добавляет имя процесса (например browser.exe) в DisallowRun."""
    cleaned = exe_name.strip()
    if not cleaned.lower().endswith(".exe"):
        raise ValueError("Укажите имя процесса в формате program.exe")

    with _open_or_create(winreg.HKEY_CURRENT_USER, EXPLORER_POLICIES) as policies_key:
        winreg.SetValueEx(policies_key, "DisallowRun", 0, winreg.REG_DWORD, 1)

    disallow_path = EXPLORER_POLICIES + r"\DisallowRun"
    with _open_or_create(winreg.HKEY_CURRENT_USER, disallow_path) as disallow_key:
        # Ищем свободный числовой ключ: "1", "2", "3"...
        idx = 1
        while True:
            name = str(idx)
            try:
                current, _ = winreg.QueryValueEx(disallow_key, name)
                if current.lower() == cleaned.lower():
                    return
                idx += 1
            except FileNotFoundError:
                winreg.SetValueEx(disallow_key, name, 0, winreg.REG_SZ, cleaned)
                return


def _normalize_domain(value: str) -> str:
    domain = value.strip().lower()
    for prefix in ("https://", "http://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.split("/")[0]
    return domain


def block_link(domain_value: str) -> str:
    """Блокирует домен через Restricted Sites (ZoneMap, зона 4)."""
    domain = _normalize_domain(domain_value)
    if not domain or "." not in domain:
        raise ValueError("Укажите корректный домен, например example.com")

    parts = domain.split(".")
    if len(parts) < 2:
        raise ValueError("Укажите корректный домен, например example.com")

    tld = parts[-1]
    second = parts[-2]
    parent = f"{second}.{tld}"

    subdomain = ".".join(parts[:-2]) if len(parts) > 2 else ""
    registry_path = f"{ZONE_MAP_DOMAINS}\\{parent}"
    if subdomain:
        registry_path += f"\\{subdomain}"

    with _open_or_create(winreg.HKEY_CURRENT_USER, registry_path) as key:
        winreg.SetValueEx(key, "*", 0, winreg.REG_DWORD, 4)

    return domain


class BlockerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Запрещатор программ и ссылок")
        self.root.geometry("500x260")
        self.root.resizable(False, False)

        frame = tk.Frame(root, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Процесс (пример: browser.exe):").pack(anchor="w")
        self.proc_entry = tk.Entry(frame, width=50)
        self.proc_entry.pack(fill="x", pady=(4, 10))

        tk.Button(
            frame,
            text="Запретить программу",
            command=self.on_block_program,
            height=2,
            bg="#d9534f",
            fg="white",
        ).pack(fill="x")

        tk.Label(frame, text="\nСсылка/домен (пример: example.com):").pack(anchor="w")
        self.link_entry = tk.Entry(frame, width=50)
        self.link_entry.pack(fill="x", pady=(4, 10))

        tk.Button(
            frame,
            text="Запретить ссылку",
            command=self.on_block_link,
            height=2,
            bg="#5b8def",
            fg="white",
        ).pack(fill="x")

        tk.Label(
            frame,
            text="Изменения записываются в HKCU (реестр текущего пользователя).",
            fg="#666",
        ).pack(anchor="w", pady=(12, 0))

    def on_block_program(self):
        value = self.proc_entry.get()
        try:
            block_program(value)
            messagebox.showinfo("Готово", f"Успешно запрещено: {value.strip()}\n\nНажмите OK")
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))

    def on_block_link(self):
        value = self.link_entry.get()
        try:
            domain = block_link(value)
            messagebox.showinfo("Готово", f"Успешно запрещено: {domain}\n\nНажмите OK")
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))


if __name__ == "__main__":
    app_root = tk.Tk()
    BlockerApp(app_root)
    app_root.mainloop()
