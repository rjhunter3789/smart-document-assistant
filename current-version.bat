@echo off
REM Shows current version from changelog

echo Looking for current version...
echo.

REM Find the last version line in the changelog
powershell -Command "Get-Content CHANGELOG_AND_RECOVERY.md | Select-String '### Version (\d+\.\d+\.\d+)' | Select-Object -Last 1"

echo.
echo Next version suggestions:
echo - For small fixes: Increment last number (3.1.1 → 3.1.2)
echo - For new features: Increment middle number (3.1.1 → 3.2.0)  
echo - For major changes: Increment first number (3.1.1 → 4.0.0)
echo.
pause