#!/bin/bash



set -e # exit immidately if any errors



if [ -z "$1"]; then
    echo "Error No folder name"
    echo "Usage ./create_module.sh <folder_name>"
    exit 1
fi


FOLDER_NAME="$1"

echo "Create directory: $FOLDER_NAME"
mkdir -p "modules/$FOLDER_NAME"



touch "modules/$FOLDER_NAME/__init__.py"
touch "modules/$FOLDER_NAME/repository.py"
touch "modules/$FOLDER_NAME/service.py"
touch "modules/$FOLDER_NAME/schemas.py"
touch "modules/$FOLDER_NAME/models.py"

echo "Done the module with $FOLDER_NAME created"



