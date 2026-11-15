"""Shared helpers to build figure decks on the CICERO PowerPoint template.

Used by build_figures_pptx.py and build_megan_pptx.py (needs python-pptx, Pillow, lxml).
Layouts (by name): Forside Farge (title), Agenda (outline), Kapittelside (section divider),
Tittel og innhold (figures, tables, text). Colours and fonts come from the template theme,
so restyling the template restyles the deck.
"""
import copy
import io
import uuid
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR as TC
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

TEMPLATE = Path(__file__).with_name("cicero_template.pptx")
BODYFONT = "+mn-lt"  # theme body font
M = 0.48  # template margin (in)
DPI = 200  # image pixels per displayed inch (capped at the original size)


class Deck:
    def __init__(self, template=TEMPLATE):
        self.prs = Presentation(template)
        self.W = self.prs.slide_width / 914400
        self.H = self.prs.slide_height / 914400
        lay = {l.name: l for l in self.prs.slide_layouts}
        self.L_TITLE, self.L_AGENDA = lay["Forside Farge"], lay["Agenda"]
        self.L_CHAPTER, self.L_FIG = lay["Kapittelside"], lay["Tittel og innhold"]
        self.sections = []  # (name, [slide ids])
        # drop the template's sample slides (unreferenced parts are not saved)
        sld_lst = self.prs.slides._sldIdLst
        for sid in list(sld_lst):
            self.prs.part.drop_rel(sid.rId)
            sld_lst.remove(sid)

    # ------------------------------------------------------------ low level
    @staticmethod
    def style(r, size, color=TC.TEXT_1, bold=None, italic=None, font=BODYFONT):
        r.font.size = Pt(size)
        if bold is not None:
            r.font.bold = bold
        if italic is not None:
            r.font.italic = italic
        if font:
            r.font.name = font
        if isinstance(color, str):
            r.font.color.rgb = RGBColor.from_string(color)
        elif color is not None:
            r.font.color.theme_color = color

    def text(self, slide, x, y, w, h, lines, size, color=TC.TEXT_1, bold=False, name=None, space_after=0):
        """Text box. A line may be (text, {"bold":…, "size":…, "color":…, "italic":…})."""
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, line in enumerate(lines if isinstance(lines, list) else [lines]):
            opt = {}
            if isinstance(line, tuple):
                line, opt = line
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            if space_after:
                p.space_after = Pt(space_after)
            r = p.add_run()
            r.text = line
            self.style(r, opt.get("size", size), opt.get("color", color), opt.get("bold", bold),
                       opt.get("italic"))
        return tb

    @staticmethod
    def fill(ph, lines, size=None, bold=None, level1=None):
        """Write lines into a placeholder; (level, text) tuples set the level."""
        tf = ph.text_frame
        for i, line in enumerate(lines if isinstance(lines, list) else [lines]):
            lvl = 0
            if isinstance(line, tuple):
                lvl, line = line
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.level = lvl
            r = p.add_run()
            r.text = line
            sz = size if lvl == 0 else (level1 or size)
            if sz:
                r.font.size = Pt(sz)
            if bold is not None and lvl == 0:
                r.font.bold = bold

    @staticmethod
    def ph(slide, idx):
        for p in slide.placeholders:
            if p.placeholder_format.idx == idx:
                return p
        raise KeyError(idx)

    @staticmethod
    def drop_empty_placeholders(slide):
        for p in list(slide.placeholders):
            if not p.has_text_frame or not p.text_frame.text.strip():
                p._element.getparent().remove(p._element)

    @staticmethod
    def add_slide_number(slide, layout):
        """python-pptx does not copy the layout's slide-number placeholder: clone it."""
        for sh in layout.placeholders:
            if sh.placeholder_format.type == 13:  # SLIDE_NUMBER
                el = copy.deepcopy(sh._element)
                ids = [int(x) for x in slide.shapes._spTree.xpath("//p:cNvPr/@id")]
                el.xpath("./p:nvSpPr/p:cNvPr")[0].set("id", str(max(ids) + 1))
                slide.shapes._spTree.append(el)
                return

    @staticmethod
    def compressed(path, box_w, box_h):
        im = Image.open(path)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            white = Image.new("RGB", im.size, (255, 255, 255))
            white.paste(im, mask=im.split()[-1])
            im = white
        else:
            im = im.convert("RGB")
        s = min(box_w / im.width, box_h / im.height)
        disp_w, disp_h = im.width * s, im.height * s
        tw = min(im.width, int(disp_w * DPI))
        if tw < im.width:
            im = im.resize((tw, round(im.height * tw / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88, subsampling=0, optimize=True)
        buf.seek(0)
        return buf, disp_w, disp_h

    def new_slide(self, section_name, layout):
        s = self.prs.slides.add_slide(layout)
        if not self.sections or self.sections[-1][0] != section_name:
            self.sections.append((section_name, []))
        self.sections[-1][1].append(s.slide_id)
        return s

    def footer(self, slide, s):
        # between the CICERO logo (bottom left) and the slide number (bottom right)
        self.text(slide, 1.85, 7.0, 10.3, 0.22, s, 9, "7F7F7F", name="Footer")

    def kicker(self, slide, s):
        self.text(slide, M, 0.22, 12.3, 0.25, s, 11, TC.TEXT_2, bold=True, name="Kicker")

    def set_title(self, slide, title):
        assert len(title) <= 96, title
        self.fill(self.ph(slide, 0), title, size=24 if len(title) <= 60 else 18)

    # ------------------------------------------------------------ slide types
    def title_slide(self, title, subtitle, info_lines):
        s = self.new_slide("Title", self.L_TITLE)
        self.fill(self.ph(s, 0), title)
        self.fill(self.ph(s, 1), subtitle, size=20)
        self.fill(self.ph(s, 12), info_lines)
        self.drop_empty_placeholders(s)
        return s

    def agenda(self, story):
        s = self.new_slide("Title", self.L_AGENDA)
        self.fill(self.ph(s, 0), "Outline")
        lines = []
        for sec in story:
            lines.append(f"{sec['num']}   {sec['title']}")
            lines.append((1, " · ".join(t for t, _ in sec["subs"])))
        body = self.ph(s, 13)
        body.width = Inches(self.W - 2 * M)  # full width: each subsection list fits on 1–2 lines
        self.fill(body, lines, size=16, bold=True, level1=11)
        self.add_slide_number(s, self.L_AGENDA)
        return s

    def divider(self, sec):
        s = self.new_slide(f"{sec['num']} {sec['title']}", self.L_CHAPTER)
        self.fill(self.ph(s, 0), f"{sec['num']}   {sec['title']}", size=32)
        self.fill(self.ph(s, 13), sec["intro"], size=20)  # layout default is 50 pt
        subs = [f"{sec['num']}.{i+1}  {t}  ({len(items)})" for i, (t, items) in enumerate(sec["subs"])]
        half = (len(subs) + 1) // 2
        self.text(s, M, 5.25, 5.7, 1.2, subs[:half], 13, TC.TEXT_2, name="Subsections 1")
        self.text(s, M + 6.0, 5.25, 5.7, 1.2, subs[half:], 13, TC.TEXT_2, name="Subsections 2")
        self.drop_empty_placeholders(s)
        return s

    def content_slide(self, sec_name, kick, title):
        s = self.new_slide(sec_name, self.L_FIG)
        self.kicker(s, kick)
        self.set_title(s, title)
        return s

    def finish(self, s, footer_text=None, notes=None):
        self.drop_empty_placeholders(s)
        self.add_slide_number(s, self.L_FIG)
        if footer_text:
            self.footer(s, footer_text)
        if notes:
            s.notes_slide.notes_text_frame.text = notes

    def picture(self, s, path, x, y, w, h):
        """Fit an image into the box (x, y, w, h), centred."""
        buf, dw, dh = self.compressed(path, w, h)
        pic = s.shapes.add_picture(buf, Inches(x + (w - dw) / 2), Inches(y + (h - dh) / 2),
                                   Inches(dw), Inches(dh))
        pic.name = Path(path).stem
        return pic, dw, dh

    def figure_slide(self, sec_name, kick, title, path, rel, notes_extra=""):
        s = self.content_slide(sec_name, kick, title)
        top, bottom = 1.6, 6.85
        self.picture(s, path, M, top, self.W - 2 * M, bottom - top)
        self.finish(s, rel, f"{title}\nFile: {rel}" + (f"\n{notes_extra}" if notes_extra else ""))
        return s

    def add_sections(self):
        P = "http://schemas.openxmlformats.org/presentationml/2006/main"
        P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
        pres = self.prs.part._element
        ext_lst = pres.find(f"{{{P}}}extLst")
        if ext_lst is None:
            ext_lst = etree.SubElement(pres, f"{{{P}}}extLst")
        uri = "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}"
        for old in ext_lst.findall(f"{{{P}}}ext[@uri='{uri}']"):
            ext_lst.remove(old)
        ext = etree.Element(f"{{{P}}}ext", uri=uri)
        ext_lst.insert(0, ext)
        lst = etree.SubElement(ext, f"{{{P14}}}sectionLst", nsmap={"p14": P14})
        for name, ids in self.sections:
            sec = etree.SubElement(lst, f"{{{P14}}}section", name=name,
                                   id="{" + str(uuid.uuid4()).upper() + "}")
            sl = etree.SubElement(sec, f"{{{P14}}}sldIdLst")
            for i in ids:
                etree.SubElement(sl, f"{{{P14}}}sldId", id=str(i))

    def save(self, out, title):
        self.add_sections()
        self.prs.core_properties.title = title
        self.prs.save(out)
