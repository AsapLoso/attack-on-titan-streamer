-- aot_aniskip.lua
-- High-visibility On-Screen "Skip Intro [Tab]" Button for MPV
local mp = require 'mp'
local utils = require 'mp.utils'

local op_start = nil
local op_end = nil
local ed_start = nil
local ed_end = nil
local skipped_op = false
local skipped_ed = false
local auto_skip = false
local overlay = mp.create_osd_overlay("ass-events")

-- Parse script-opts passed from python/cli
local function parse_opts()
    local opts = mp.get_opt("aot_skip")
    if opts then
        for k, v in string.gmatch(opts, "([%w_]+)=([%d%.]+)") do
            if k == "op_start" then op_start = tonumber(v) end
            if k == "op_end" then op_end = tonumber(v) end
            if k == "ed_start" then ed_start = tonumber(v) end
            if k == "ed_end" then ed_end = tonumber(v) end
            if k == "auto_skip" then auto_skip = (v == "1") end
        end
    end
end

-- Key binding to Skip Intro / Outro
local function perform_skip()
    local pos = mp.get_property_number("time-pos")
    if not pos then return end
    
    if op_start and op_end and pos >= (op_start - 2) and pos < op_end then
        mp.commandv("seek", op_end, "absolute")
        mp.osd_message("⏩ Opening Skipped", 2)
        skipped_op = true
        overlay:remove()
    elseif ed_start and ed_end and pos >= (ed_start - 2) and pos < ed_end then
        mp.commandv("seek", ed_end, "absolute")
        mp.osd_message("⏩ Ending Skipped", 2)
        skipped_ed = true
        overlay:remove()
    else
        mp.commandv("seek", 85, "relative")
        mp.osd_message("⏩ Fast-Forward +85s", 1.5)
    end
end

-- Timer to check current position and render visual on-screen button
local function check_skip_time()
    local pos = mp.get_property_number("time-pos")
    if not pos then 
        overlay:remove()
        return 
    end
    
    -- Opening check
    if op_start and op_end and pos >= op_start and pos < op_end then
        if auto_skip and not skipped_op then
            mp.commandv("seek", op_end, "absolute")
            mp.osd_message("⏩ Opening Auto-Skipped", 2)
            skipped_op = true
            overlay:remove()
        elseif not skipped_op then
            local rem = math.ceil(op_end - pos)
            -- Render a prominent Netflix-style button on the bottom right
            overlay.data = "{\\an3\\fs22\\bord3\\b1\\c&H00FFFF&\\3c&H111111&\\shad1\\pos(1240,670)}  ⏩ Skip Opening (Press TAB)  "
            overlay:update()
        else
            overlay:remove()
        end
    -- Ending check
    elseif ed_start and ed_end and pos >= ed_start and pos < ed_end then
        if not skipped_ed then
            overlay.data = "{\\an3\\fs22\\bord3\\b1\\c&H00FFFF&\\3c&H111111&\\shad1\\pos(1240,670)}  ⏩ Skip Ending (Press TAB)  "
            overlay:update()
        else
            overlay:remove()
        end
    else
        overlay:remove()
    end
end

mp.add_key_binding("TAB", "aot_skip_intro", perform_skip)
mp.add_key_binding("s", "aot_skip_intro_s", perform_skip)
mp.add_key_binding("S", "aot_skip_intro_shift_s", perform_skip)

-- When clicked on screen
mp.add_key_binding("MBTN_LEFT", "aot_click_skip", function()
    local pos = mp.get_property_number("time-pos")
    if pos and op_start and op_end and pos >= op_start and pos < op_end and not skipped_op then
        perform_skip()
    else
        mp.commandv("cycle", "pause")
    end
end)

mp.register_event("file-loaded", function()
    skipped_op = false
    skipped_ed = false
    overlay:remove()
    parse_opts()
end)

mp.add_periodic_timer(0.2, check_skip_time)
