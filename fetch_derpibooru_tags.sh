#!/bin/bash

set -e

while [ -n "$1" ]; do
    [ -e "$1".tags ] && shift && continue
    file_hash=$(sha512sum "$1" | cut -d ' ' -f 1 )
    wget -O - "https://derpibooru.org/search.json?q=orig_sha512_hash%3A$file_hash" | grep -m 1 --only-matching '"tags":".\+","tag_ids":' | cut -d '"' -f '4' > "$1".tags
    grep -q ',' "$1".tags || rm "$1".tags
    shift
done
