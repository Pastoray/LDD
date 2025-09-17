#!/bin/bash

echo "Starting entrypoint..."
export DISPLAY=:1
XVFB_SCREEN_RES="1080x2460x24"
Xvfb $DISPLAY -screen 0 $XVFB_SCREEN_RES +extension RANDR >/dev/null 2>&1 &
sleep 2

ollama serve >/dev/null 2>&1 &
sleep 5

openbox-session
