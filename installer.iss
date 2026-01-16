; dayzopenlauncher inno setup script

#define AppBaseVersion "1.1.0"
#define AppBuildDate "14.01.2026"
#define AppBuildNum "1"
#define AppVersionCode 202601141

[Setup]
AppId={{2CDE692F-4309-47F1-949B-52951F232B2B}}
AppName=DayzOpenLauncher
AppVersion={#AppBaseVersion} ({#AppBuildDate}) {#AppBuildNum}
AppVerName=DayzOpenLauncher {#AppBaseVersion}
UninstallDisplayName=DayzOpenLauncher
AppPublisher=PawelKawka
AppPublisherURL=https://github.com/PawelKawka/DayzOpenLauncher
AppUpdatesURL=https://github.com/PawelKawka/PawelKawka/releases

DefaultDirName={localappdata}\DayzOpenLauncher
DefaultGroupName=DayzOpenLauncher
UninstallDisplayIcon={app}\icon.ico

OutputDir=.
OutputBaseFilename=DayzOpenLauncher_Setup
SetupIconFile=assets\icon.ico
SolidCompression=yes
Compression=lzma2/max

DirExistsWarning=no
UsePreviousAppDir=yes

WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DayzOpenLauncher\DayzOpenLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DayzOpenLauncher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "assets\*"

[Icons]
Name: "{group}\DayzOpenLauncher"; Filename: "{app}\DayzOpenLauncher.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\DayzOpenLauncher"; Filename: "{app}\DayzOpenLauncher.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Registry]
Root: HKCU; Subkey: "Software\DayzOpenLauncher"; ValueType: string; ValueName: "VersionString"; ValueData: "{#AppBaseVersion} ({#AppBuildDate}) {#AppBuildNum}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\DayzOpenLauncher"; ValueType: dword; ValueName: "VersionCode"; ValueData: "{#AppVersionCode}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\DayzOpenLauncher.exe"; Description: "{cm:LaunchProgram,DayzOpenLauncher}"; Flags: nowait postinstall skipifsilent

[Code]
var
  MaintenancePage: TInputOptionWizardPage;
  IsUpdateMode: Boolean;
  IsReinstallOnly: Boolean;

const
  InternalKey = 'Software\DayzOpenLauncher';
  AppIdKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{2CDE692F-4309-47F1-949B-52951F232B2B}_is1';
  LegacyKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\DayzOpenLauncher_is1';

function IsInstalled: Boolean;
begin
  Result := RegKeyExists(HKEY_CURRENT_USER, InternalKey) or
            RegKeyExists(HKEY_CURRENT_USER, AppIdKey) or
            RegKeyExists(HKEY_LOCAL_MACHINE, AppIdKey) or
            RegKeyExists(HKEY_CURRENT_USER, LegacyKey) or
            RegKeyExists(HKEY_LOCAL_MACHINE, LegacyKey) or
            FileExists(ExpandConstant('{localappdata}\DayzOpenLauncher\DayzOpenLauncher.exe'));
end;

function GetInstalledVersionCode: Cardinal;
var
  VCode: Cardinal;
begin
  Result := 0;
  if RegQueryDWordValue(HKEY_CURRENT_USER, InternalKey, 'VersionCode', VCode) then begin Result := VCode; Exit; end;
end;

function GetInstalledVersionString: String;
var
  Ver: String;
begin
  Result := 'Unknown';
  if RegQueryStringValue(HKEY_CURRENT_USER, InternalKey, 'VersionString', Ver) then if Ver <> '' then begin Result := Ver; Exit; end;
  if RegQueryStringValue(HKEY_CURRENT_USER, AppIdKey, 'DisplayVersion', Ver) then if Ver <> '' then begin Result := Ver; Exit; end;
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, AppIdKey, 'DisplayVersion', Ver) then if Ver <> '' then begin Result := Ver; Exit; end;
  if GetVersionNumbersString(ExpandConstant('{localappdata}\DayzOpenLauncher\DayzOpenLauncher.exe'), Ver) then if Ver <> '' then begin Result := Ver; Exit; end;
end;

procedure InitializeWizard;
var
  InstalledVer: String;
  InstalledCode, CurrentCode: Cardinal;
begin
  IsUpdateMode := False;
  IsReinstallOnly := False;
  
  if IsInstalled then
  begin
    IsUpdateMode := True;
    InstalledVer := GetInstalledVersionString;
    InstalledCode := GetInstalledVersionCode;
    CurrentCode := {#AppVersionCode};
    
    MaintenancePage := CreateInputOptionPage(wpWelcome,
      'Maintenance', 'Existing Installation Detected',
      'Select maintenance operation.' + #13#10 +
      'Installed: ' + InstalledVer + ' | New: {#AppBaseVersion} ({#AppBuildDate}) {#AppBuildNum}',
      True, False);

    if (InstalledCode > 0) and (InstalledCode >= CurrentCode) then
    begin
      MaintenancePage.Add('Reinstall (Repair current version)');
      IsReinstallOnly := True;
    end
    else
    begin
      MaintenancePage.Add('Update (Recommended)');
      MaintenancePage.Add('Reinstall (Clean install)');
    end;
    MaintenancePage.SelectedValueIndex := 0;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  AppDir: String;
  CleanNeeded: Boolean;
begin
  CleanNeeded := False;
  
  if IsUpdateMode then
  begin
    if IsReinstallOnly then
      CleanNeeded := True
    else if MaintenancePage.SelectedValueIndex = 1 then
      CleanNeeded := True;
  end;

  if CleanNeeded then
  begin
    AppDir := ExpandConstant('{app}');
    if (Length(AppDir) > 3) and DirExists(AppDir) then
    begin
      DelTree(AppDir + '\*', False, True, True);
    end;
  end;
  
  Result := '';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if IsUpdateMode then
  begin
    if PageID = wpSelectDir then
    begin
      Result := True;
      Exit;
    end;

    if (PageID = wpSelectTasks) and (not IsReinstallOnly) and (MaintenancePage.SelectedValueIndex = 0) then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin

  if CurStep = ssInstall then
  begin
    if RegKeyExists(HKEY_CURRENT_USER, LegacyKey) then
      RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, LegacyKey);
    if RegKeyExists(HKEY_LOCAL_MACHINE, LegacyKey) then
      RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, LegacyKey);
  end;
end;
