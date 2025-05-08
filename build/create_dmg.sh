
set -e

APP_NAME="QR2Key"
APP_VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${APP_VERSION}"
BUILD_DIR="$(pwd)/dist"
DMG_DIR="$(pwd)/dist/dmg"
APP_PATH="${BUILD_DIR}/${APP_NAME}.app"

if ! command -v create-dmg &> /dev/null; then
    echo "Error: create-dmg is not installed"
    echo "Please install it with: brew install create-dmg"
    exit 1
fi

if [ ! -d "$APP_PATH" ]; then
    echo "Error: PyInstaller build not found at $APP_PATH"
    echo "Please run PyInstaller first"
    exit 1
fi

mkdir -p "$DMG_DIR"

echo "Creating DMG installer..."
create-dmg \
    --volname "$APP_NAME" \
    --volicon "src/resources/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "$APP_NAME.app" 175 190 \
    --hide-extension "$APP_NAME.app" \
    --app-drop-link 425 190 \
    --no-internet-enable \
    "${DMG_DIR}/${DMG_NAME}.dmg" \
    "$APP_PATH"

echo "DMG installer created at ${DMG_DIR}/${DMG_NAME}.dmg"
