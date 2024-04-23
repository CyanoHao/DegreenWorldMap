if GetLocale() == "enUS" then return end

function RefreshOverlaysHook(pin, fullUpdate)
	local mapID = pin:GetMap():GetMapID()
	if not mapID then return end
	-- print("mapID = " .. mapID)
	if not OverrideMapList[mapID] then return end

	local mapArtLayerInfo = C_Map.GetMapArtLayers(mapID)[1]
	local width = mapArtLayerInfo.layerWidth
	local height = mapArtLayerInfo.layerHeight
	local nCols = ceil(width / 256)
	local nRows = ceil(height / 256)

	for row = 0, nRows - 1 do
		for col = 0, nCols - 1 do
			local texture = pin.overlayTexturePool:Acquire()
			texture:SetWidth(256)
			texture:SetHeight(256)
			texture:SetTexCoord(0, 1, 0, 1)
			texture:SetPoint("TOPLEFT", 256 * col, -256 * row)
			texture:SetTexture("Interface/AddOns/DegreenWorldMap/Tiles/" .. mapID .. "/" .. (row * nCols + col) .. ".jpg" , nil, nil, "TRILINEAR")

			texture:SetDrawLayer("ARTWORK", 1)
			texture:Show()
			pin.textureLoadGroup:AddTexture(texture)
		end
	end
end

function Init()
	for pin in WorldMapFrame:EnumeratePinsByTemplate("MapExplorationPinTemplate") do
		hooksecurefunc(pin, "RefreshOverlays", RefreshOverlaysHook)
	end
end

Init()
