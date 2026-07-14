"""?????TXT / EPUB"""
import os
from typing import Dict, List, Optional
from datetime import datetime

class NovelExporter:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
        os.makedirs(self.output_dir, exist_ok=True)

    def export_txt(self, novel_data: Dict, filename: str = None) -> str:
        title = novel_data.get("title", "?????")
        author = novel_data.get("author", "")
        chapters = novel_data.get("chapters", [])
        outline = novel_data.get("outline", {})

        lines = []
        lines.append(f"\u3000\u3000{title}")
        if author:
            lines.append(f"\u3000\u3000???{author}")
        lines.append("")

        if outline:
            outline_text = outline.get("content", "") if isinstance(outline, dict) else str(outline)
            lines.append("=" * 40)
            lines.append("??")
            lines.append("=" * 40)
            lines.append(outline_text)
            lines.append("")

        for ch in chapters:
            ch_title = ch.get("title", f"?{ch.get('chapter_number', 0)}?")
            lines.append("=" * 40)
            lines.append(f"\u3000\u3000{ch_title}")
            lines.append("=" * 40)
            content = ch.get("content", "")
            lines.append(content)
            lines.append("")

        text = "\n".join(lines)
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip() or "novel"
        fn = filename or f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.output_dir, fn)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return filepath

    def export_epub(self, novel_data: Dict, filename: str = None) -> str:
        title = novel_data.get("title", "?????")
        author = novel_data.get("author", "")
        chapters = novel_data.get("chapters", [])

        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip() or "novel"
        fn = filename or f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        import hashlib
        uid = hashlib.md5((title + datetime.now().isoformat()).encode()).hexdigest()[:16]

        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">')
        lines.append(f'  <metadata>')
        lines.append(f'    <dc:title>{title}</dc:title>')
        if author:
            lines.append(f'    <dc:creator>{author}</dc:creator>')
        lines.append(f'    <dc:identifier id="BookId">{uid}</dc:identifier>')
        lines.append(f'    <dc:language>zh-CN</dc:language>')
        lines.append(f'    <meta name="generator" content="Soultext v0.1.0" />')
        lines.append(f'  </metadata>')
        lines.append(f'  <manifest>')
        lines.append(f'    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />')
        lines.append(f'    <item id="content" href="content.xhtml" media-type="application/xhtml+xml" />')
        lines.append(f'  </manifest>')
        lines.append(f'  <spine toc="ncx">')
        lines.append(f'    <itemref idref="content" />')
        lines.append(f'  </spine>')
        lines.append(f'</package>')

        # NCX
        ncx = []
        ncx.append('<?xml version="1.0" encoding="UTF-8"?>')
        ncx.append('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">')
        ncx.append(f'  <head><meta name="dtb:uid" content="{uid}"/></head>')
        ncx.append(f'  <docTitle><text>{title}</text></docTitle>')
        ncx.append(f'  <navMap>')
        for i, ch in enumerate(chapters):
            ch_title = ch.get("title", f"?{ch.get('chapter_number', i+1)}?")
            ncx.append(f'    <navPoint id="ch{i}" playOrder="{i+1}"><navLabel><text>{ch_title}</text></navLabel><content src="content.xhtml#ch{i}"/></navPoint>')
        ncx.append(f'  </navMap>')
        ncx.append(f'</ncx>')

        # XHTML content
        xhtml = []
        xhtml.append('<?xml version="1.0" encoding="UTF-8"?>')
        xhtml.append('<!DOCTYPE html>')
        xhtml.append('<html xmlns="http://www.w3.org/1999/xhtml">')
        xhtml.append(f'<head><title>{title}</title><meta charset="UTF-8"/></head>')
        xhtml.append('<body>')
        xhtml.append(f'<h1>{title}</h1>')
        if author:
            xhtml.append(f'<p>???{author}</p>')
        for i, ch in enumerate(chapters):
            ch_title = ch.get("title", f"?{ch.get('chapter_number', i+1)}?")
            content = ch.get("content", "")
            xhtml.append(f'<h2 id="ch{i}">{ch_title}</h2>')
            for para in content.split("\n\n"):
                if para.strip():
                    xhtml.append(f'<p>{para.replace("\n", "<br/>")}</p>')
        xhtml.append('</body></html>')

        # Write EPUB (ZIP)
        import zipfile
        filepath = os.path.join(self.output_dir, fn.replace(".txt", ".epub"))
        with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
            zf.writestr("OEBPS/content.opf", "\n".join(lines).encode("utf-8"))
            zf.writestr("OEBPS/toc.ncx", "\n".join(ncx).encode("utf-8"))
            zf.writestr("OEBPS/content.xhtml", "\n".join(xhtml).encode("utf-8"))
        return filepath

    def export(self, novel_data: Dict, fmt: str = "txt") -> str:
        if fmt == "epub":
            return self.export_epub(novel_data)
        return self.export_txt(novel_data)
