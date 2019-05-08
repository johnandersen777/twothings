#!/usr/bin/env bash
set -xe

mkdir -p ~/.local/share/systemd/user/
cp twothings/assests/systemd/* ~/.local/share/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now twothings-calendar-sync
