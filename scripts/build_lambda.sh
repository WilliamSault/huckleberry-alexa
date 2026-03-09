#!/usr/bin/env bash
# Build a Lambda deployment zip for the Huckleberry Alexa skill.
# Requires: uv
# Usage: bash scripts/build_lambda.sh

set -euo pipefail

DIST_DIR="dist/lambda_package"
ZIP_FILE="deployment.zip"

echo "==> Cleaning previous build..."
rm -rf "$DIST_DIR" "$ZIP_FILE"
mkdir -p "$DIST_DIR"

echo "==> Installing dependencies for x86_64-manylinux2014..."
uv pip install \
  --target "$DIST_DIR" \
  --python-platform x86_64-manylinux2014 \
  --python 3.12 \
  ask-sdk-core \
  huckleberry-api \
  aiohttp \
  pytz

echo "==> Copying source package..."
cp -r src/huckleberry_alexa "$DIST_DIR/"

echo "==> Creating deployment.zip..."
cd "$DIST_DIR"
zip -r "../../$ZIP_FILE" . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*"
cd ../..

ZIP_SIZE=$(du -sh "$ZIP_FILE" | cut -f1)
echo ""
echo "==> Done! $ZIP_FILE ($ZIP_SIZE)"
echo ""

# Warn if over 50MB direct upload limit
SIZE_BYTES=$(stat -f%z "$ZIP_FILE" 2>/dev/null || stat -c%s "$ZIP_FILE" 2>/dev/null)
if [ "$SIZE_BYTES" -gt 52428800 ]; then
  echo "WARNING: $ZIP_FILE exceeds 50MB. Use S3 to upload:"
  echo "  aws s3 cp $ZIP_FILE s3://YOUR_BUCKET/$ZIP_FILE"
  echo "  aws lambda update-function-code --function-name huckleberry-alexa \\"
  echo "    --s3-bucket YOUR_BUCKET --s3-key $ZIP_FILE"
else
  echo "Upload with:"
  echo "  aws lambda update-function-code --function-name huckleberry-alexa \\"
  echo "    --zip-file fileb://$ZIP_FILE"
fi
