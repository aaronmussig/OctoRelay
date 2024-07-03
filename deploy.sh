#!/usr/bin/env bash
target="pi@pi.local";
echo "deploy to octopi: ${target}"
rsync -avzh octoprint_octorelaypi5/ --delete ${target}:~/oprint/lib/python3.9/site-packages/octoprint_octorelaypi5
