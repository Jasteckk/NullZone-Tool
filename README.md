# NullZone Account Manager

Compact WinForms interface for managing saved Steam sessions.

## v1.3 redesign

- Loads the public Steam display name from each Steam ID and shows it beside the avatar.
- Keeps the original imported username internally, so login, export and account removal behavior is unchanged.
- Caches profile names locally alongside avatar images, with the imported username as an offline fallback.

- Deeper near-black theme with cleaner contrast
- Larger NullZone logo and simplified sidebar
- Dedicated Discord-themed **JOIN DISCORD** button opening `https://discord.gg/nullzone`
- Rebuilt custom button rendering to prevent blue hover/focus corner artifacts
- Wider, full-text Steam action buttons
- Clearer export action and improved spacing throughout
- Steam profile pictures load asynchronously and are cached under `%LocalAppData%\NullZone\AvatarCache`
- Account initials remain as an automatic fallback when offline or when Steam does not return an avatar
- Existing import, login, export, Steam control, backup, restore, drag/drop, clipboard, and context-menu behavior retained
- Accounts started through NullZone are switched to **Invisible** automatically after the Steam Friends service is ready; the login flow is not blocked if the status command fails

## Requirements

- Windows 10/11 x64
- .NET 8 SDK

## Preview from Visual Studio

Open `NullZone.sln`, then press `Ctrl+F5`.

## Build and publish the EXE

Double-click `build-release.bat`, or run:

```powershell
dotnet restore .\NullZone.sln
dotnet build .\NullZone.sln -c Release
dotnet publish .\NullZoneTool\NullZoneTool.csproj -c Release -r win-x64 --self-contained false
```

Published executable:

```text
NullZoneTool\bin\Release\net8.0-windows\win-x64\publish\NullZone.exe
```

Avatar retrieval is isolated from login and Steam-management logic. A failed or slow avatar request never blocks account import or login. Core account and Steam-management functions remain unchanged.
