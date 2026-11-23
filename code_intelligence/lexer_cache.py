# Bounded prefix checkpoints for GUI-owned Python and Markdown lexers.
# Positions are UTF-8 bytes offsets. These caches are used only by the GUI thread.
# They must never be chared between editor documents or different scanner backends.

from bisect import bisect_left, bisect_right


def common_prefix_length(left: bytes, right: bytes) -> int:
    """
    Return the number of identical leading bytes using C-level comparisions.
    
    A binary search avoids a Python iteration per source byte. Prefix slices do
    allocate memory; this is a transitional snapshot cache, not a rope or an 
    edit-delta buffer. The worst case still copies 0(n log n) bytes per revision.
    It does not work on individual keystrokes until styling requests a snapshot.
    """
    low, high = 0, min(len(left), len(right))
    while low < high:
        middle = (low + high + 1) // 2
        if left[:middle] == right[:middle]:
            low = middle
        else:
            high = middle - 1
    return low


class PrefixCache:
    """
    Own one immutable source snapshot and resumable incoming states.
    
    A state at p describes the scanner immediately BEFORE byte p. Entries are
    backend-specific opaque values. Zero is always a safe fallback. Changed
    suffixes are discarded rather than shifted or guessed to remain valid.
    """
    
    def __init__(self, initial_state=None, limit: int = 512):
        """Create an empty cache; limit includes the permanent zero entry."""
        if limit < 2:
            raise ValueError("limit must include zero and at least one checkpoint")
        self.source = b""
        self.initial_state = initial_state
        self.states = {0: initial_state}
        self.limit = limit
        
    
    def replace(self, source:bytes) -> None:
        """Install a snapshot and discard states possibly by its edits.
        
        Keep only checkpoints strictly before the changed line and four bytes
        of lookahead. This conservative rewind covers quote/prefix recognition
        in the current scanner. Insertion, deletion and replacement use the same
        rule, so no notification-order assumtion or edits-potitions shifts are 
        required. Equal snapshot leavr all checkpoints intact.
        """
        if source == self.source:
            return
        matched = common_prefix_length(self.source, source)
        safe = source.rfind(b"\n", 0, max(0, matched - 4)) + 1
        self.states = {p: state for p, state in self.states.items() if p < safe}
        self.states[0] = self.initial_state
        self.source = source
        
    
    def nearest(self, target: int):
        """Return (position, state) for the closest checkpoint at/before target."""
        position = max(p for p in self.states if p <= max(0, target))
        return position, self.states[position]
    
    
    def trim(self) -> None:
        """Keep zero plus the highest offsets within the configured capacity.
        
        Eviction affects speed, never correctness: an ecioted range is rescanned
        from an earlier checkpoint. This policy favors continued downward edits.
        """
        excess = len(self.states) - self.limit
        if excess > 0:
            for position in sorted(self.states)[1:excess + 1]:
                del self.states[position]
                

class PythonCheckpointCache(PrefixCache):
    """Resume the existing prefix scanner without changing token style IDs."""
    
    def state_before(self, target: int, scanner, *, resumable: bool = True):
        """Return packed style flags at target and retin complete checkpoints.
        
        scanner(source, target, snapshot, checkpoints) restores every live 
        prefix-scanner variable. Its return value remains the original packed
        flags expected by style-chunks. Old compiled extensions accept only two
        arguments: resumable=False keeps that path correct until rebuilt.
        """
        target = min(max(0, target), len(self.source))
        if not resumable:
            return scanner(self.source, target)
        _, snapshot = self.nearest(target)
        result = scanner(self.source, target, snapshot, self.states)
        self.trim()
        return result
    

class MarkdownLineCache(PrefixCache):
    """Index LF-delimited Markdown lines and cache incoming fence/comment state."""
    
    
    def __init__(self, limit: int = 512):
        """Use the existing Markdown scanner's four-value initial state."""
        super().__init__((False, None, 0, False), limit)
        self.starts = [0]
        
        
    def replace(self, source: bytes) -> None:
        """Rebuild byte line offsets only when immutable snapshot changes.
        
        LF and CRLF are preserved exactly. CR remains part of a line body, as in 
        the previous lexer. A trailing LF creates and empty final line at EOF.
        """
        if source == self.source:
            return
        super().replace(source)
        self.starts = [0]
        position = source.find(b"\n")
        while position >= 0:
            self.starts.append(position + 1)
            position = source.find(b"\n", position + 1)
        
    
    def line_at(self, position:int) -> int:
        """Map a clamped byte position to its zero-based containing line."""
        return bisect_right(self.starts, min(max(position, 0), len(self.source))) - 1
    
    
    def lines_to(self, start:int, end:int) -> int:
        """Yield (being, next_begin, body, has_lf) for complete affected lines.
        
        start must be a cached line boundary. Including the whole final line
        preserves inline token context when QScintilla requests a partial range.
        The generator does not style or mutate states; the owning lexer does.
        """
        first = bisect_left(self.starts, start)
        last = self.line_at(max(start, end - 1))
        for index in range(first, last + 1):
            begin = self.starts[index]
            next_begin = (self.starts[index + 1] if index + 1 < len(self.starts) else len(self.source))
            raw = self.source[begin:next_begin]
            has_lf = raw.endswith(b"\n")
            body = raw[:-1] if has_lf else raw
            yield begin, next_begin, body.decode("utf-8"), has_lf
        

