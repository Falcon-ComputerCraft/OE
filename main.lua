local settings = {
    ["GithubURL"] = "https://github.com/Falcon-ComputerCraft/Falcon-OE"
}

-- Scrolls the terminal content down by the given number of lines.
-- @param y Number of lines to scroll; positive values move content down, negative values move it up.
local function scrollDown(y)
    term.scroll(-y)
end

print("                   Falcon OE")
scrollDown(3)
print(settings["GithubURL"])