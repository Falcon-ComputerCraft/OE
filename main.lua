local settings = {
    ["GithubURL"] = "https://github.com/Falcon-ComputerCraft/Falcon-OE"
}

local function scrollDown(y)
    term.scroll(-y)
end

print("                   Falcon OE")
scrollDown(3)
print(settings["GithubURL"])