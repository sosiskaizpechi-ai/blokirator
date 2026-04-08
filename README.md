# Запрещатор программ и ссылок (Windows)

Простое GUI-приложение на Python (`tkinter`) для Windows:

- Блокирует запуск программ по имени процесса (например `browser.exe`) через реестр:
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun`
- Блокирует домены/ссылки через Restricted Sites (ZoneMap) в реестре:
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains`
- После успешного запрета показывает сообщение с кнопкой **OK**.

## Запуск

1. Установите Python 3 на Windows.
2. Сохраните файл `blocker_windows.py`.
3. Запустите:

```powershell
python blocker_windows.py
```

## Важно

- Для работы с реестром используются права текущего пользователя (HKCU), поэтому запуск от администратора обычно не нужен.
- Некоторые ограничения могут применяться не мгновенно: иногда требуется перелогиниться или перезапустить `explorer.exe`.
- Приложение демонстрационное; перед использованием на рабочей машине рекомендуется создать точку восстановления.
blocker_windows.py
blocker_windows.py
