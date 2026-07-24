@echo off
setlocal
cd /d "%~dp0"

dotnet restore NullZone.sln
if errorlevel 1 exit /b 1

dotnet build NullZone.sln -c Release
if errorlevel 1 exit /b 1

dotnet publish NullZoneTool\NullZoneTool.csproj -c Release -r win-x64 --self-contained false
if errorlevel 1 exit /b 1

echo.
echo Build complete.
echo Output: NullZoneTool\bin\Release\net8.0-windows\win-x64\publish
pause
