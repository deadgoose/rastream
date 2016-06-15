#!/bin/sh
# Example of script for using mpv with youtube-dl
set -e

cookies_dir="$(mktemp -d /tmp/youtube-dl_mpv.XXXX)"
cookies_file="${cookies_dir}/cookies"
user_agent="$(youtube-dl --dump-user-agent)" # or set whatever you want

video_url="$(youtube-dl \
    --user-agent="$user_agent" \
    --cookies="$cookies_file" \
    --get-url \
    "$1")"

echo $video_url
