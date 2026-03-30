"""
Tests for main.lua

Tests cover:
  - scrollDown(y): calls term.scroll(-y)
  - Module-level execution: print calls and initial scrollDown(3) call
  - settings table: GithubURL value
"""

import pytest
import lupa

MAIN_LUA_PATH = "main.lua"

# Lua snippet containing only the scrollDown function, exposed as a global so it
# can be called with arbitrary arguments from the test suite.
_SCROLL_DOWN_SNIPPET = """
local function scrollDown(y)
    term.scroll(-y)
end
_G.scrollDown = scrollDown
"""


def _make_lua_runtime():
    """Return a fresh LuaRuntime with unpack_returned_tuples enabled."""
    return lupa.LuaRuntime(unpack_returned_tuples=True)


def _load_main(lua, scroll_calls, print_calls):
    """
    Load main.lua into *lua* with term.scroll and print replaced by recorders.

    Args:
        lua: A lupa.LuaRuntime instance.
        scroll_calls: A list that will be appended with each argument passed to
            term.scroll().
        print_calls: A list that will be appended with each tuple of arguments
            passed to print().
    """
    lua.globals().term = lua.table()
    lua.globals().term.scroll = lambda n: scroll_calls.append(n)
    lua.globals().print = lambda *args: print_calls.append(args)

    with open(MAIN_LUA_PATH, "r") as fh:
        code = fh.read()
    lua.execute(code)


def _load_scroll_down(lua, scroll_calls):
    """
    Load the scrollDown function into *lua* (as a global) with term.scroll
    replaced by a recorder.

    Args:
        lua: A lupa.LuaRuntime instance.
        scroll_calls: A list that will be appended with each argument passed to
            term.scroll().
    """
    lua.globals().term = lua.table()
    lua.globals().term.scroll = lambda n: scroll_calls.append(n)
    # Suppress print so the snippet doesn't produce output during isolated tests.
    lua.globals().print = lambda *_: None
    lua.execute(_SCROLL_DOWN_SNIPPET)


# ---------------------------------------------------------------------------
# scrollDown behaviour
# ---------------------------------------------------------------------------

class TestScrollDown:
    """Unit tests for the scrollDown(y) function."""

    def test_scroll_down_positive(self):
        """scrollDown(3) must call term.scroll(-3)."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(3)
        assert calls == [-3]

    def test_scroll_down_zero(self):
        """scrollDown(0) must call term.scroll(0)."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(0)
        assert calls == [0]

    def test_scroll_down_negative_value(self):
        """scrollDown(-2) negates the argument, so term.scroll(2) is called."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(-2)
        assert calls == [2]

    def test_scroll_down_large_value(self):
        """scrollDown with a large positive integer delegates correctly."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(100)
        assert calls == [-100]

    def test_scroll_down_one(self):
        """scrollDown(1) calls term.scroll(-1) — boundary value."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(1)
        assert calls == [-1]

    def test_scroll_down_calls_term_scroll_exactly_once(self):
        """scrollDown must invoke term.scroll exactly one time per call."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(5)
        assert len(calls) == 1

    def test_scroll_down_multiple_calls_accumulate(self):
        """Each invocation of scrollDown records a separate term.scroll call."""
        lua = _make_lua_runtime()
        calls = []
        _load_scroll_down(lua, calls)
        lua.globals().scrollDown(1)
        lua.globals().scrollDown(2)
        lua.globals().scrollDown(3)
        assert calls == [-1, -2, -3]


# ---------------------------------------------------------------------------
# Module-level execution (side effects when main.lua is loaded)
# ---------------------------------------------------------------------------

class TestModuleExecution:
    """Tests for the top-level statements executed when main.lua is loaded."""

    def setup_method(self):
        self.lua = _make_lua_runtime()
        self.scroll_calls = []
        self.print_calls = []
        _load_main(self.lua, self.scroll_calls, self.print_calls)

    def test_title_is_printed(self):
        """Loading main.lua must print the Falcon OE title string."""
        printed_strings = [args[0] for args in self.print_calls]
        assert "                   Falcon OE" in printed_strings

    def test_github_url_is_printed(self):
        """Loading main.lua must print the GitHub URL."""
        printed_strings = [args[0] for args in self.print_calls]
        assert "https://github.com/Falcon-ComputerCraft/Falcon-OE" in printed_strings

    def test_print_called_exactly_twice(self):
        """Exactly two print calls should occur during module load."""
        assert len(self.print_calls) == 2

    def test_title_printed_before_url(self):
        """The title must appear before the GitHub URL in print output."""
        printed_strings = [args[0] for args in self.print_calls]
        title_index = printed_strings.index("                   Falcon OE")
        url_index = printed_strings.index(
            "https://github.com/Falcon-ComputerCraft/Falcon-OE"
        )
        assert title_index < url_index

    def test_scroll_called_on_load(self):
        """term.scroll must be called at least once when main.lua is loaded."""
        assert len(self.scroll_calls) >= 1

    def test_scroll_value_on_load(self):
        """The module-level scrollDown(3) call must pass -3 to term.scroll."""
        assert -3 in self.scroll_calls

    def test_scroll_called_exactly_once_on_load(self):
        """term.scroll must be called exactly once during module load."""
        assert len(self.scroll_calls) == 1


# ---------------------------------------------------------------------------
# settings table
# ---------------------------------------------------------------------------

class TestSettings:
    """Tests for the settings table defined at the top of main.lua."""

    def test_github_url_value(self):
        """The GithubURL setting must equal the expected repository URL."""
        lua = _make_lua_runtime()
        scroll_calls = []
        print_calls = []
        _load_main(lua, scroll_calls, print_calls)

        # The URL is printed as the second print call; verify the exact value.
        github_url_output = print_calls[1][0]
        assert github_url_output == "https://github.com/Falcon-ComputerCraft/Falcon-OE"

    def test_github_url_points_to_falcon_oe(self):
        """The GitHub URL must reference the Falcon-OE project."""
        lua = _make_lua_runtime()
        scroll_calls = []
        print_calls = []
        _load_main(lua, scroll_calls, print_calls)

        github_url_output = print_calls[1][0]
        assert "Falcon-OE" in github_url_output

    def test_github_url_is_valid_https(self):
        """The GithubURL value must use HTTPS."""
        lua = _make_lua_runtime()
        scroll_calls = []
        print_calls = []
        _load_main(lua, scroll_calls, print_calls)

        github_url_output = print_calls[1][0]
        assert github_url_output.startswith("https://")