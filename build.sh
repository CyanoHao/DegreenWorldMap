#!/bin/bash

export DXVK_LOG_LEVEL=none

function Clean() {
	rm -r DegreenWorldMap/Tiles/
}

function GenerateOverrideMapListLua() {
	set -e
	local overrideMapListLua=DegreenWorldMap/OverrideMapList.lua
	echo "OverrideMapList = {" >$overrideMapListLua
	awk '{ print "\t[" $1 "] = true," }' <map-info.txt >>$overrideMapListLua
	echo "}" >>$overrideMapListLua
}

function GenerateMapTile() {
	local mapID=$1
	local mapFile=$2
	local dim=$(magick identify gallery/$mapFile | grep -oE " [0-9]+x[0-9]+ ")
	local height=${dim#*x}
	local outDir=DegreenWorldMap/Tiles/$mapID
	mkdir -p $outDir
	if (( $height == 2560 )) ; then
		# 3840×2560, split to 15x10 256x256 tiles
		magick gallery/$mapFile -crop 256x256 -quality 80 $outDir/%d.jpg
	else
		# 1002×668, extend to 1024x768 and then split to 4x3 256x256 tiles
		magick gallery/$mapFile -background black -extent 1024x768 -crop 256x256 -quality 80 $outDir/%d.jpg
	fi
}

function GenerateAllMap() {
	local line
	local mapID
	local mapFile
	local nCPU=$(nproc)
	local running=0
	while read line ; do
		(( ++running % nCPU == 0 )) && wait
		mapID=$(cut -f1 <<<$line)
		mapFile=$(cut -f2 <<<$line)
		GenerateMapTile $mapID $mapFile &
	done
	wait
}

function Package() {
	local version=$(cat DegreenWorldMap/DegreenWorldMap.toc | grep "^## Version" | cut -d' ' -f3)
	local packageFile=DegreenWorldMap-$version.zip
	rm $packageFile || true
	zip -r $packageFile DegreenWorldMap/
}

Clean
GenerateOverrideMapListLua
GenerateAllMap <map-info.txt
Package
