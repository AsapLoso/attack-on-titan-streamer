-- aot_aniskip.lua
-- On-screen "Skip Intro [Tab]" button and AniSkip handler for MPV
local mp = require 'mp'
local utils = require 'mp.utils'

local op_start = nil
local op_end = nil
local ed_start = nil
local ed_end = nil
local skipped_op = false
local skipped_ed = false
local auto_skip = false

-- Function to parse script-opts passed from python/cli
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
    elseif ed_start and ed_end and pos >= (ed_start - 2) and pos < ed_end then
        mp.commandv("seek", ed_end, "absolute")
        mp.osd_message("⏩ Ending Skipped", 2)
        skipped_ed = true
    else
        -- Fallback: forward 85s
        mp.commandv("seek", 85, "relative")
        mp.osd_message("⏩ Fast-Forward +85s", 1.5)
    end
end

-- Periodic timer to check current position and show button or auto-skip
local function check_skip_time()
    local pos = mp.get_property_number("time-pos")
    if not pos then return end
    
    -- Opening check
    if op_start and op_end and pos >= op_start and pos < op_end then
        if auto_skip and not skipped_op then
            mp.commandv("seek", op_end, "absolute")
            mp.osd_message("⏩ Opening Auto-Skipped", 2)
            skipped_op = true
        elseif not skipped_op then
            local remaining = math.ceil(op_end - pos)
            mp.osd_message("⏩ [Tab] Skip Opening (" .. remaining .. "s)", 1.0)
        end
    end
    
    -- Ending check
    if ed_start and ed_end and pos >= ed_start and pos < ed_end then
        if not skipped_ed then
            local remaining = math.ceil(ed_end - pos)
            mp.osd_message("⏩ [Tab] Skip Ending (" .. remaining .. "s)", 1.0)
        end
    end
end

mp.add_key_binding("TAB", "aot_skip_intro", perform_skip)
mp.add_key_binding("s", "aot_skip_intro_s", perform_skip)
mp.add_key_binding("S", "aot_skip_intro_shift_s", perform_skip)

mp.register_event("file-loaded", function()
    skipped_op = false
    skipped_ed = false
    parse_opts()
end)

mp.add_periodic_timer(0.5, check_skip_time)
