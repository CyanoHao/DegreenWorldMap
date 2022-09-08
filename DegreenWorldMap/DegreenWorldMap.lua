if GetLocale() == "enUS" then return end

function RefreshOverlaysHook(pin, fullUpdate)
	local mapID = pin:GetMap():GetMapID()
	if not mapID then return end
	-- print("mapID = " .. mapID)
	if not OverrideMapList[mapID] then return end

	local width = HighResMapList[mapID] and 3840 or 1002
	local height = HighResMapList[mapID] and 2560 or 668

	for row = 0, 1 do
		for col = 0, 2 do
			local texture = pin.overlayTexturePool:Acquire()
			texture:SetWidth(width / 3)
			texture:SetHeight(height / 2)
			texture:SetTexCoord(0, 1, 0, 1)
			texture:SetPoint("TOPLEFT", width * col / 3, -height * row / 2)
			texture:SetTexture("Interface/AddOns/DegreenWorldMap/Tiles/" .. mapID .. "/" .. (row * 3 + col) .. ".jpg" , nil, nil, "TRILINEAR")

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
