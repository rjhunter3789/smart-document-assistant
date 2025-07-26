@echo off
REM Windows batch file for updating changelog

set /p VERSION="Enter version number (e.g., 3.1.1): "
set /p DESCRIPTION="Enter brief description: "

echo. >> CHANGELOG_AND_RECOVERY.md
echo ### Version %VERSION% - %date% >> CHANGELOG_AND_RECOVERY.md
echo. >> CHANGELOG_AND_RECOVERY.md
echo **Changes:** >> CHANGELOG_AND_RECOVERY.md
echo - %DESCRIPTION% >> CHANGELOG_AND_RECOVERY.md
echo. >> CHANGELOG_AND_RECOVERY.md
echo **Commit:** >> CHANGELOG_AND_RECOVERY.md
git log -1 --pretty=format:"- %%h - %%s" >> CHANGELOG_AND_RECOVERY.md
echo. >> CHANGELOG_AND_RECOVERY.md
echo. >> CHANGELOG_AND_RECOVERY.md

git add CHANGELOG_AND_RECOVERY.md
git commit -m "Update changelog for v%VERSION%"

echo Changelog updated! Don't forget to push.