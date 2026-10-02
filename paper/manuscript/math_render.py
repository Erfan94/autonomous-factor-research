"""Typeset the manuscript's mathematics for both outputs.

Display equations (`!eq` lines) are written in a small LaTeX subset and emitted as MathML for the PDF
(Chrome renders MathML Core) and as OMML for the DOCX (Word's native equation format). Inline math in
prose is written between \\( and \\) and emitted as italic/subscript text in the body font, so it matches
the surrounding Times.

Subset: identifiers ([A-Za-z]+ digits*, or one Greek letter), numbers, operators, {groups}, _ and ^,
\\frac{a}{b}, \\sum (limits under/over, operand = following terms up to + − = ,), \\left( ... \\right),
\\mathrm{...}, \\beta, \\cdot, \\times, \\, (thin space). A one-letter identifier is italic; a longer one
(LS, LRV, D10, rf) is upright.
"""
import html
import re

_TOK = re.compile(r"\\[A-Za-z]+|\\,|[A-Za-z]+\d*|[α-ωΑ-Ω]|\d+(?:\.\d+)?|\S")
_GREEK = {"beta": "β", "alpha": "α", "sigma": "σ", "mu": "μ", "rho": "ρ"}
_OPS = {"cdot": "·", "times": "×"}


def _tokens(s):
    return _TOK.findall(s)


class _P:
    def __init__(self, s):
        self.t = _tokens(s)
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def row(self, stop=None):
        out = []
        while self.peek() is not None and self.peek() != stop:
            out.append(self.term())
        return ("row", out)

    def group_raw(self):
        assert self.take() == "{"
        out = []
        while self.peek() != "}":
            out.append(self.take())
        self.take()
        return "".join(out)

    def atom(self):
        tok = self.take()
        if tok == "{":
            r = self.row("}")
            self.take()
            return r
        if tok == "\\frac":
            return ("frac", self.atom(), self.atom())
        if tok == "\\mathrm":
            return ("id", self.group_raw(), False)
        if tok == "\\left":
            o = self.take()
            inner = []
            while self.peek() != "\\right":
                inner.append(self.term())
            self.take()
            c = self.take()
            return ("fence", o, c, ("row", inner))
        if tok == "\\sum":
            return ("sumop",)
        if tok == "\\,":
            return ("space",)
        if tok.startswith("\\"):
            name = tok[1:]
            if name in _GREEK:
                return ("id", _GREEK[name], True)
            if name in _OPS:
                return ("op", _OPS[name])
            raise ValueError(f"unsupported command {tok}")
        if re.fullmatch(r"\d+(?:\.\d+)?", tok):
            return ("num", tok)
        if re.fullmatch(r"[A-Za-z]+\d*|[α-ωΑ-Ω]", tok):
            return ("id", tok, len(tok) == 1)
        return ("op", "−" if tok == "-" else tok)

    def term(self):
        base = self.atom()
        sub = sup = None
        while self.peek() in ("_", "^"):
            if self.take() == "_":
                sub = self.atom()
            else:
                sup = self.atom()
        if base[0] == "sumop":
            body = []
            while self.peek() is not None and self.peek() not in ("+", "-", "−", "=", ",", "}", "\\right"):
                body.append(self.term())
            return ("nary", "∑", sub, sup, ("row", body))
        if sub is not None and sup is not None:
            return ("subsup", base, sub, sup)
        if sub is not None:
            return ("sub", base, sub)
        if sup is not None:
            return ("sup", base, sup)
        return base


def parse(s):
    return _P(s).row()


# ----------------------------------------------------------------------------- MathML
def _mml(n, script=False):
    k = n[0]
    if k == "row":
        return "<mrow>" + "".join(_mml(c, script) for c in n[1]) + "</mrow>"
    if k == "id":
        v = html.escape(n[1])
        return f"<mi>{v}</mi>" if n[2] else f"<mi mathvariant='normal'>{v}</mi>"
    if k == "num":
        return f"<mn>{n[1]}</mn>"
    if k == "op":
        tight = " lspace='0' rspace='0'" if script else ""
        return f"<mo{tight}>{html.escape(n[1])}</mo>"
    if k == "space":
        return "<mspace width='0.17em'/>"
    if k == "frac":
        return f"<mfrac>{_mml(n[1])}{_mml(n[2])}</mfrac>"
    if k == "sub":
        return f"<msub>{_mml(n[1], script)}{_mml(n[2], True)}</msub>"
    if k == "sup":
        return f"<msup>{_mml(n[1], script)}{_mml(n[2], True)}</msup>"
    if k == "subsup":
        return f"<msubsup>{_mml(n[1], script)}{_mml(n[2], True)}{_mml(n[3], True)}</msubsup>"
    if k == "fence":
        return (f"<mrow><mo stretchy='true'>{html.escape(n[1])}</mo>{_mml(n[3])}"
                f"<mo stretchy='true'>{html.escape(n[2])}</mo></mrow>")
    if k == "nary":
        lo = _mml(n[2], True) if n[2] else "<mrow/>"
        hi = _mml(n[3], True) if n[3] else "<mrow/>"
        return f"<mrow><munderover><mo largeop='true' movablelimits='false'>∑</mo>{lo}{hi}</munderover>{_mml(n[4])}</mrow>"
    raise ValueError(k)


def mathml(s):
    return f"<math display='block'>{_mml(parse(s))}</math>"


# ----------------------------------------------------------------------------- OMML
_W_FONT = "<w:rPr><w:rFonts w:ascii='Cambria Math' w:hAnsi='Cambria Math'/></w:rPr>"


def _mr(text, upright=False):
    sty = "<m:rPr><m:sty m:val='p'/></m:rPr>" if upright else ""
    return f"<m:r>{sty}{_W_FONT}<m:t xml:space='preserve'>{html.escape(text)}</m:t></m:r>"


def _om(n):
    k = n[0]
    if k == "row":
        return "".join(_om(c) for c in n[1])
    if k == "id":
        return _mr(n[1], upright=not n[2])
    if k in ("num", "op"):
        return _mr(n[1])
    if k == "space":
        return _mr(" ")
    if k == "frac":
        return f"<m:f><m:num>{_om(n[1])}</m:num><m:den>{_om(n[2])}</m:den></m:f>"
    if k == "sub":
        return f"<m:sSub><m:e>{_om(n[1])}</m:e><m:sub>{_om(n[2])}</m:sub></m:sSub>"
    if k == "sup":
        return f"<m:sSup><m:e>{_om(n[1])}</m:e><m:sup>{_om(n[2])}</m:sup></m:sSup>"
    if k == "subsup":
        return f"<m:sSubSup><m:e>{_om(n[1])}</m:e><m:sub>{_om(n[2])}</m:sub><m:sup>{_om(n[3])}</m:sup></m:sSubSup>"
    if k == "fence":
        return (f"<m:d><m:dPr><m:begChr m:val='{html.escape(n[1])}'/><m:endChr m:val='{html.escape(n[2])}'/></m:dPr>"
                f"<m:e>{_om(n[3])}</m:e></m:d>")
    if k == "nary":
        lo = _om(n[2]) if n[2] else ""
        hi = _om(n[3]) if n[3] else ""
        return (f"<m:nary><m:naryPr><m:chr m:val='∑'/><m:limLoc m:val='undOvr'/></m:naryPr>"
                f"<m:sub>{lo}</m:sub><m:sup>{hi}</m:sup><m:e>{_om(n[4])}</m:e></m:nary>")
    raise ValueError(k)


def omml_para(s):
    """An m:oMathPara element (as XML text with namespaces declared) for one display equation."""
    return ("<m:oMathPara xmlns:m='http://schemas.openxmlformats.org/officeDocument/2006/math' "
            "xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>"
            f"<m:oMath>{_om(parse(s))}</m:oMath></m:oMathPara>")


# ----------------------------------------------------------------------------- inline
INLINE = re.compile(r"\\\((.+?)\\\)")


def inline_segments(s, vert=None):
    """[(text, italic, vert)] for inline math: one-letter identifiers italic, scripts as sub/superscript."""
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "_^":
            v = "sub" if ch == "_" else "sup"
            if s[i + 1] == "{":
                j = s.index("}", i + 2)
                inner, i = s[i + 2:j], j + 1
            else:
                m = re.match(r"[A-Za-z]+\d*|[α-ωΑ-Ω]|\d+|.", s[i + 1:])
                inner, i = m.group(0), i + 1 + len(m.group(0))
            out += inline_segments(inner, v)
            continue
        m = re.match(r"[A-Za-z]+\d*|[α-ωΑ-Ω]", s[i:])
        if m:
            w = m.group(0)
            out.append((w, len(w) == 1, vert))
            i += len(w)
            continue
        out.append(({"-": "−", " ": "\u00a0"}.get(ch, ch), False, vert))
        i += 1
    merged = []
    for seg in out:
        if merged and merged[-1][1:] == seg[1:]:
            merged[-1] = (merged[-1][0] + seg[0],) + seg[1:]
        else:
            merged.append(seg)
    return merged


def inline_html(s):
    parts = []
    for text, it, vert in inline_segments(s):
        h = html.escape(text, quote=False)
        if it:
            h = f"<i>{h}</i>"
        if vert:
            h = f"<{vert}>{h}</{vert}>"
        parts.append(h)
    return "".join(parts)
