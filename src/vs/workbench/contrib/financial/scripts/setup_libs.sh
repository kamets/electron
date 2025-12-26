#!/bin/bash
# Links user provided libraries to the local environment

TARGET_DIR="$(dirname "$0")/../external_libs"
mkdir -p "$TARGET_DIR"

declare -a LIBS=(
    "/mnt/c/Users/NAMAN/matplotlib"
    "/mnt/c/Users/NAMAN/pyAudit"
    "/mnt/c/Users/NAMAN/AI-Insurance-Fraud-Detection"
    "/mnt/c/Users/NAMAN/dspy"
    "/mnt/c/Users/NAMAN/supabase"
    "/mnt/c/Users/NAMAN/Accounting"
    "/mnt/c/Users/NAMAN/docling_docConvert"
)

echo "Linking libraries to $TARGET_DIR..."

for lib in "${LIBS[@]}"; do
    if [ -d "$lib" ]; then
        name=$(basename "$lib")
        ln -sfn "$lib" "$TARGET_DIR/$name"
        echo "Linked: $name"
    else
        echo "Warning: Not found: $lib"
    fi
done

echo "Library setup complete."
ls -l "$TARGET_DIR"
