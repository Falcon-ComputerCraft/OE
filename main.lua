local unitTestsEnabled = false
local settings = {
    ["GithubURL"] = "https://github.com/Falcon-ComputerCraft/Falcon-OE"
}

-- Scrolls the terminal content down by the given number of lines.
-- @param y Number of lines to scroll; positive values move content down, negative values move it up.
local function scrollDown(y)
    term.scroll(-y)
end

-- UNIT TESTS START

if unitTestsEnabled == true then
    print("Running unit tests...")
    print("Running visualUnitTest for scrollDown()")
    scrollDown(3)
    print("Confirm if the terminal content has scrolled down by 3 lines.")
    print("Unit tests completed.")
    sleep(3)
    print("Stopping program.")
    return
end

-- UNIT TESTS END

print("                   Falcon OE")
scrollDown(3)
print(settings["GithubURL"])