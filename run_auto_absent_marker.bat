@echo off
cd /d E:\attendance-system
"C:\Program Files\Python312\python.exe" auto_absent_marker.py

echo %DATE% %TIME% >> E:\attendance-system\absent_task_log.txt