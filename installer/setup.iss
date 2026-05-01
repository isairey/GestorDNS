; Instalador profesional de OneClickDNS
; Versión PRO optimizada - Junio 2025

[Setup]
AppName=OneClickDNS
AppVersion=1.0.1
AppPublisher=gfrodriguez
AppPublisherURL=https://github.com/gfrodriguez/OneClickDNS
AppSupportURL=https://github.com/gfrodriguez/OneClickDNS/issues
AppUpdatesURL=https://github.com/gfrodriguez/OneClickDNS/releases
DefaultDirName={autopf}\OneClickDNS
DefaultGroupName=OneClickDNS
OutputBaseFilename=OneClickDNS_Setup
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
RestartIfNeededByRun=False
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\assets\icons\icon.ico
UninstallDisplayIcon={app}\assets\icons\icon.ico
WizardStyle=modern
AllowCancelDuringInstall=yes
AlwaysShowDirOnReadyPage=yes
DisableWelcomePage=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Ejecutable principal
Source: "..\dist\OneClickDNS.exe"; DestDir: "{app}"; Flags: ignoreversion

; Recursos gráficos
Source: "..\assets\icons\*"; DestDir: "{app}\assets\icons"; Flags: recursesubdirs createallsubdirs
Source: "..\assets\screenshots\*"; DestDir: "{app}\assets\screenshots"; Flags: recursesubdirs createallsubdirs

; Manual en HTML (mejor para usuario)
Source: "..\docs\manual.html"; DestDir: "{app}\docs"; Flags: isreadme

; (Si mantienes manual.md, puedes eliminar esta línea o convertirlo a HTML)

[Run]
Filename: "{app}\OneClickDNS.exe"; Description: "Iniciar OneClickDNS"; Flags: nowait postinstall skipifsilent runascurrentuser

[Icons]
Name: "{group}\OneClickDNS"; Filename: "{app}\OneClickDNS.exe"; IconFilename: "{app}\assets\icons\icon.ico"
Name: "{autodesktop}\OneClickDNS"; Filename: "{app}\OneClickDNS.exe"; IconFilename: "{app}\assets\icons\icon.ico"; Tasks: desktopicon

[UninstallRun]
; Ejecuta el script de limpieza de DNS
Filename: "{app}\reset_dns.bat"; Flags: runhidden

[InstallDelete]
Type: files; Name: "{app}\log_dns.txt"

[Code]
// Comprobación de privilegios al iniciar el instalador
procedure InitializeWizard();
begin
  if not IsAdminLoggedOn() then
  begin
    MsgBox('Esta aplicación requiere permisos de administrador para modificar la configuración de red.', mbError, MB_OK);
    Abort();
  end;
end;