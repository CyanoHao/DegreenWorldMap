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
	local dim=$(magick identify gallery/$2 | grep -oE " [0-9]+x[0-9]+ ")
	local height=${dim#*x}
	local tempFile1=$(mktemp --suffix=.png)
	local tempFile2=$(mktemp --suffix=.png)
	local outDir=DegreenWorldMap/Tiles/$mapID
	mkdir -p $outDir

	if (( $height > 2048 )) ; then
		# FSR 3840×2560 → 6144×4096
		bin/FidelityFX_CLI.exe -Mode EASU -Scale 6144 4096 gallery/$mapFile $tempFile1
		bin/FidelityFX_CLI.exe -Mode RCAS -Sharpness 0.2 $tempFile1 $tempFile2
		# split to 3×2 2048×2048 tiles
		for row in 0 1 ; do
			for col in 0 1 2 ; do
				magick $tempFile2 -crop 2048x2048+$((2048*$col))+$((2048*row)) -quality 80 $outDir/$(($row*3+$col)).jpg
			done
		done
	else
		# FSR 1002×668 → 1754×1170 → 3072×2048
		bin/FidelityFX_CLI.exe -Mode EASU -Scale 1754 1170 gallery/$mapFile $tempFile1
		bin/FidelityFX_CLI.exe -Mode RCAS -Sharpness 0.2 $tempFile1 $tempFile2
		bin/FidelityFX_CLI.exe -Mode EASU -Scale 3072 2048 $tempFile2 $tempFile1
		bin/FidelityFX_CLI.exe -Mode RCAS -Sharpness 0.2 $tempFile1 $tempFile2
		# split to 3×2 1024×1024 tiles
		for row in 0 1 ; do
			for col in 0 1 2 ; do
				magick $tempFile2 -crop 1024x1024+$((1024*$col))+$((1024*row)) -quality 80 $outDir/$(($row*3+$col)).jpg
			done
		done
	fi
	rm $tempFile1
	rm $tempFile2
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
