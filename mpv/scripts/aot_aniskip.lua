-- aot_aniskip.lua
-- Bulletproof AniSkip On-Screen Skip Button for MPV
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

-- Helper to find episodes.json
local function load_episodes_data()
    local dir = mp.get_script_directory()
    local paths = {
        utils.join_path(dir, "episodes.json"),
        utils.join_path(dir, "../../episodes.json"),
        utils.join_path(dir, "../episodes.json"),
        "C:\\Users\\Deuts\\OneDrive - Delft University of Technology\\Misc\\Gemini\\AOT\\episodes.json"
    }
    
    for _, p in ipairs(paths) do
        local f = io.open(p, "r")
        if f then
            local content = f:read("*all")
            f:close()
            local success, data = pcall(utils.parse_json, content)
            if success and data then
                return data
            end
        end
    end
    return nil
end

local function init_timestamps()
    local opt_op_s = mp.get_opt("op_start") or mp.get_opt("aot_op_start")
    local opt_op_e = mp.get_opt("op_end") or mp.get_opt("aot_op_end")
    local opt_ed_s = mp.get_opt("ed_start") or mp.get_opt("aot_ed_start")
    local opt_ed_e = mp.get_opt("ed_end") or mp.get_opt("aot_ed_end")
    local opt_auto = mp.get_opt("auto_skip")
    
    if opt_op_s and opt_op_e then
        op_start = tonumber(opt_op_s)
        op_end = tonumber(opt_op_e)
        if opt_ed_s then ed_start = tonumber(opt_ed_s) end
        if opt_ed_e then ed_end = tonumber(opt_ed_e) end
        auto_skip = (opt_auto == "1")
        mp.msg.info(string.format("Loaded timestamps from CLI: OP %s -> %s", op_start, op_end))
        return
    end

    local path = mp.get_property("path", "")
    local filename = mp.get_property("filename", "")
    local data = load_episodes_data()
    
    if data then
        for _, ep in ipairs(data) do
            local ep_fn = ep.filename or ""
            local ep_url = ep.stream_url or ""
            if (filename ~= "" and string.find(filename, ep_fn, 1, true)) or 
               (path ~= "" and string.find(path, ep_fn, 1, true)) or
               (ep_url ~= "" and path == ep_url) then
                local ts = ep.timestamps or {}
                if ts.op_start and ts.op_end then
                    op_start = tonumber(ts.op_start)
                    op_end = tonumber(ts.op_end)
                    ed_start = tonumber(ts.ed_start)
                    ed_end = tonumber(ts.ed_end)
                    mp.msg.info(string.format("Matched episode %s from JSON: OP %s -> %s", ep.id, op_start, op_end))
                    return
                end
            end
        end
    end
end

local function perform_skip()
    local pos = mp.get_property_number("time-pos")
    if not pos then return end
    
    if op_start and op_end and pos >= (op_start - 5) and pos < op_end then
        mp.commandv("seek", op_end, "absolute")
        mp.osd_message("⏩ Opening Skipped", 2)
        skipped_op = true
        overlay:remove()
    elseif ed_start and ed_end and pos >= (ed_start - 5) and pos < ed_end then
        mp.commandv("seek", ed_end, "absolute")
        mp.osd_message("⏩ Ending Skipped", 2)
        skipped_ed = true
        overlay:remove()
    else
        mp.commandv("seek", 85, "relative")
        mp.osd_message("⏩ Fast-Forward +85s", 1.5)
    end
end

local function check_skip_time()
    local pos = mp.get_property_number("time-pos")
    if not pos then 
        overlay:remove()
        return 
    end
    
    if op_start and op_end and pos >= op_start and pos < op_end then
        if auto_skip and not skipped_op then
            mp.commandv("seek", op_end, "absolute")
            mp.osd_message("⏩ Opening Auto-Skipped", 2)
            skipped_op = true
            overlay:remove()
        elseif not skipped_op then
            local rem = math.ceil(op_end - pos)
            overlay.data = "{\\an3\\fs24\\bord3\\b1\\c&H00E5FF&\\3c&H000000&\\shad2\\pos(1240,660)} [ ⏩ Skip Opening (Press TAB) ] "
            overlay:update()
        else
            overlay:remove()
        end
    elseif ed_start and ed_end and pos >= ed_start and pos < ed_end then
        if not skipped_ed then
            overlay.data = "{\\an3\\fs24\\bord3\\b1\\c&H00E5FF&\\3c&H000000&\\shad2\\pos(1240,660)} [ ⏩ Skip Ending (Press TAB) ] "
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

mp.register_event("file-loaded", function()
    skipped_op = false
    skipped_ed = false
    overlay:remove()
    op_start = nil
    op_end = nil
    ed_start = nil
    ed_end = nil
    init_timestamps()
end)

mp.add_periodic_timer(0.25, check_skip_time)
