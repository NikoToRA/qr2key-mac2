
set -e

APP_NAME="QR2Key"
APP_VERSION="1.0.0"
SPEC_FILE="build/spec_mac.yml"
MAIN_SCRIPT="src/main.py"

if ! python -c "import PyInstaller" &> /dev/null; then
    echo "Error: PyInstaller is not installed"
    echo "Please install it with: pip install pyinstaller"
    exit 1
fi

echo "Cleaning previous build..."
rm -rf dist build/*.spec

echo "Creating PyInstaller spec file..."
cat > "${APP_NAME}.spec" << EOF

block_cipher = None

a = Analysis(
    ['${MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[('src/config.json', 'src'), ('src/resources', 'src/resources')],
    hiddenimports=['pynput.keyboard._darwin', 'rumps'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='${APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='${APP_NAME}',
)

app = BUNDLE(
    coll,
    name='${APP_NAME}.app',
    icon='src/resources/icon.icns',
    bundle_identifier='com.qr2key.app',
    info_plist={
        'CFBundleShortVersionString': '${APP_VERSION}',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'NSHighResolutionCapable': 'True',
        'LSUIElement': '1',  # Makes the app a background app with no dock icon
    },
)
EOF

echo "Building application with PyInstaller..."
pyinstaller "${APP_NAME}.spec" --clean

echo "Build completed successfully!"
echo "Application bundle created at dist/${APP_NAME}.app"
