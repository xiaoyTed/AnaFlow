#!/bin/bash

# Build script for Next.js standalone deployment
# This script ensures all static assets are properly included

echo "Building Next.js application..."
npm run build

echo "Copying static assets to standalone build..."
cp -r .next/static .next/standalone/.next/

echo "Standalone build is ready!"
echo "To run the server: cd .next/standalone && node server.js" 