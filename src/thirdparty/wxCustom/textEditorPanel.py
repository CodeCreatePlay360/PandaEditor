import wx
import wx.richtext as rt
import xml.etree.ElementTree as ET
from io import StringIO
from io import BytesIO
from wxCustom.wxCustomPanel import WxScrolledPanel
from wxCustom.MediaPanel import ImageTile
from constants import *

ID_BOLD = wx.NewId()
ID_ITALIC = wx.NewId()
ID_ALIGN_CENTER = wx.NewId()


class TextEditorPanel(WxScrolledPanel):
    OPTIONS = [("Bold", -1, TEXT_ALIGN_CENTER),
               ("Italic", -2, TEXT_ALIGN_CENTER),
               ("ALIGN_CENTER", -3, TEXT_ALIGN_CENTER)]

    def __init__(self, parent, label, style, color):
        WxScrolledPanel.__init__(self, parent, label, style, color)
        self.create_layout()
        self.create_buttons()
        object_manager.add_object("TextEditor", self)

        self.rich_text_control = rt.RichTextCtrl(self.base_panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.rich_text_control.SetBackgroundColour(color)
        wx.CallAfter(self.rich_text_control.SetFocus)
        '''
        self.rich_text_control.Freeze()
        self.rich_text_control.BeginSuppressUndo()
        self.rich_text_control.BeginParagraphSpacing(0, 20)
        self.rich_text_control.Thaw()

        self.rich_text_control.Freeze()
        self.rich_text_control.BeginSuppressUndo()

        self.rich_text_control.BeginParagraphSpacing(0, 20)

        self.rich_text_control.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
        self.rich_text_control.BeginBold()

        self.rich_text_control.BeginFontSize(14)
        self.rich_text_control.WriteText("Welcome to wxRichTextCtrl, a wxWidgets control for editing and presenting "
                           "styled text and images")
        self.rich_text_control.EndFontSize()
        self.rich_text_control.Newline()

        self.rich_text_control.BeginItalic()
        self.rich_text_control.WriteText("by Julian Smart")
        self.rich_text_control.EndItalic()

        self.rich_text_control.EndBold()
        self.rich_text_control.EndParagraphSpacing()
        self.rich_text_control.EndSuppressUndo()
        self.rich_text_control.Thaw()
        
        self.rtc.Newline()
        # self.rtc.WriteImage(images._rt_zebra.GetImage())

        self.rtc.EndAlignment()

        self.rtc.Newline()
        self.rtc.Newline()

        self.rtc.WriteText("What can you do with this thing? ")
        # self.rtc.WriteImage(images._rt_smiley.GetImage())
        self.rtc.WriteText(" Well, you can change text ")

        self.rtc.BeginTextColour((255, 0, 0))
        self.rtc.WriteText("colour, like this red bit.")
        self.rtc.EndTextColour()

        self.rtc.BeginTextColour((0, 0, 255))
        self.rtc.WriteText(" And this blue bit.")
        self.rtc.EndTextColour()

        self.rtc.WriteText(" Naturally you can make things ")
        self.rtc.BeginBold()
        self.rtc.WriteText("bold ")
        self.rtc.EndBold()
        self.rtc.BeginItalic()
        self.rtc.WriteText("or italic ")
        self.rtc.EndItalic()
        self.rtc.BeginUnderline()
        self.rtc.WriteText("or underlined.")
        self.rtc.EndUnderline()

        self.rtc.BeginFontSize(14)
        self.rtc.WriteText(" Different font sizes on the same line is allowed, too.")
        self.rtc.EndFontSize()

        self.rtc.WriteText(" Next we'll show an indented paragraph.")

        self.rtc.BeginLeftIndent(60)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. "
                           "An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLeftIndent()

        self.rtc.Newline()

        self.rtc.WriteText("Next, we'll show a first-line indent, achieved using BeginLeftIndent(100, -40).")

        self.rtc.BeginLeftIndent(100, -40)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. "
                           "An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLeftIndent()

        self.rtc.Newline()

        self.rtc.WriteText("Numbered bullets are possible, again using sub-indents:")

        self.rtc.BeginNumberedBullet(1, 100, 60)
        self.rtc.Newline()

        self.rtc.WriteText("This is my first item. Note that wxRichTextCtrl doesn't automatically do numbering, " \
                           "but this will be added later.")

        self.rtc.EndNumberedBullet()

        self.rtc.BeginNumberedBullet(2, 100, 60)
        self.rtc.Newline()

        self.rtc.WriteText("This is my second item.")
        self.rtc.EndNumberedBullet()

        self.rtc.Newline()

        self.rtc.WriteText("The following paragraph is right-indented:")

        self.rtc.BeginRightIndent(200)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. " \
                           "An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndRightIndent()

        self.rtc.Newline()

        self.rtc.WriteText("The following paragraph is right-aligned with 1.5 line spacing:")

        self.rtc.BeginAlignment(wx.TEXT_ALIGNMENT_RIGHT)
        self.rtc.BeginLineSpacing(wx.TEXT_ATTR_LINE_SPACING_HALF)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. " \
                           "An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLineSpacing()
        self.rtc.EndAlignment()

        self.rtc.Newline()
        self.rtc.WriteText("Other notable features of wxRichTextCtrl include:")

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Compatibility with wxTextCtrl API")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Easy stack-based BeginXXX()...EndXXX() style setting in addition to SetStyle()")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("XML loading and saving")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Undo/Redo, with batching option and Undo suppressing")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Clipboard copy and paste")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("wxRichTextStyleSheet with named character and paragraph styles, and control for " \
                           "applying named styles")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("A design that can easily be extended to other content types, ultimately with text " \
                           "boxes, tables, controls, and so on")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()

        # Make a style suitable for showing a URL
        # urlStyle = rt.TextAttrEx()
        urlStyle = rt.RichTextAttr()
        urlStyle.SetTextColour(wx.BLUE)
        urlStyle.SetFontUnderlined(True)

        self.rtc.WriteText("RichTextCtrl can also display URLs, such as this one: ")
        self.rtc.BeginStyle(urlStyle)
        self.rtc.BeginURL("http://wxPython.org/")
        self.rtc.WriteText("The wxPython Web Site")
        self.rtc.EndURL()
        self.rtc.EndStyle()
        self.rtc.WriteText(". Click on the URL to generate an event.")

        self.rtc.Bind(wx.EVT_TEXT_URL, self.OnURL)

        self.rtc.Newline()
        self.rtc.WriteText("Note: this sample content was generated programmatically from within the "
                           "MyFrame constructor "
                           "in the demo. The images were loaded from inline XPMs. Enjoy wxRichTextCtrl!")


        '''

        self.create_toolbar()
        self.base_panel_sizer.Add(self.rich_text_control, 1, wx.EXPAND)
        self.Layout()

    def create_toolbar(self):
        pass

    def OnURL(self, evt):
        wx.MessageBox(evt.GetString(), "URL Clicked")

    def OnFileViewHTML(self, evt):
        # Get an instance of the html file handler, use it to save the
        # document to a StringIO stream, and then display the
        # resulting html text in a dialog with a HtmlWindow.
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7, 9, 11, 12, 14, 22, 100])

        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.rich_text_control.GetBuffer(), stream):
            return

        import wx.html
        dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        html = wx.html.HtmlWindow(dlg, size=(500, 400), style=wx.BORDER_SUNKEN)
        html.SetPage(stream.getvalue())
        btn = wx.Button(dlg, wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 10)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)

        dlg.ShowModal()
        handler.DeleteTemporaryImages()

    bold = False

    def on_bold(self):
        if self.bold is False:
            self.rich_text_control.ApplyBoldToSelection()
            self.bold = True
        else:
            self.rich_text_control.EndBold()
            self.bold = False

    italic = False

    def on_italic(self):
        if self.italic is False:
            self.rich_text_control.ApplyItalicToSelection()
            self.italic = True
        else:
            self.rich_text_control.EndItalic()
            self.italic = False

    def OnUnderline(self, evt):
        self.rich_text_control.ApplyUnderlineToSelection()

    def OnAlignLeft(self, evt):
        self.rich_text_control.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_LEFT)

    def OnAlignRight(self, evt):
        self.rich_text_control.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_RIGHT)

    def OnAlignCenter(self):
        self.rich_text_control.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_CENTRE)

    def OnIndentMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.rich_text_control.SetStyle(r, attr)

    def OnIndentLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.rich_text_control.SetStyle(r, attr)

    def OnParagraphSpacingMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
            self.rich_text_control.SetStyle(r, attr)

    def OnParagraphSpacingLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
                self.rich_text_control.SetStyle(r, attr)

    def OnLineSpacingSingle(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.rich_text_control.SetStyle(r, attr)

    def OnLineSpacingHalf(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.rich_text_control.SetStyle(r, attr)

    def OnLineSpacingDouble(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rich_text_control.GetInsertionPoint()
        if self.rich_text_control.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rich_text_control.HasSelection():
                r = self.rich_text_control.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.rich_text_control.SetStyle(r, attr)

    def OnFont(self, evt):
        if not self.rich_text_control.HasSelection():
            return

        r = self.rich_text_control.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_FONT)
        if self.rich_text_control.GetStyle(self.rich_text_control.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(wx.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rich_text_control.SetStyle(r, attr)
        dlg.Destroy()

    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if self.rich_text_control.GetStyle(self.rich_text_control.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.rich_text_control.HasSelection():
                    self.rich_text_control.BeginTextColour(colour)
                else:
                    r = self.rich_text_control.GetSelectionRange()
                    attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.rich_text_control.SetStyle(r, attr)
        dlg.Destroy()

    def OnUpdateBold(self, evt):
        evt.Check(self.rich_text_control.IsSelectionBold())

    def OnUpdateItalic(self, evt):
        evt.Check(self.rich_text_control.IsSelectionItalics())

    def OnUpdateUnderline(self, evt):
        evt.Check(self.rich_text_control.IsSelectionUnderlined())

    def OnUpdateAlignLeft(self, evt):
        evt.Check(self.rich_text_control.IsSelectionAligned(wx.TEXT_ALIGNMENT_LEFT))

    def OnUpdateAlignCenter(self, evt):
        evt.Check(self.rich_text_control.IsSelectionAligned(wx.TEXT_ALIGNMENT_CENTRE))

    def OnUpdateAlignRight(self, evt):
        evt.Check(self.rich_text_control.IsSelectionAligned(wx.TEXT_ALIGNMENT_RIGHT))

    def create_buttons(self):
        self.buttons = []
        btn = ImageTile(
            parent=self.buttons_panel,
            label="",
            style=wx.BORDER_NONE,
            color=DARK_GREY,
            size=(24, 24),
            position=(0, 0),
            tile_index=-1
        )
        btn.set_image(TEXT_ALIGN_CENTER, fixed=True)
        self.buttons.append(btn)

        self.btn_sizer.AddSpacer(1)

    def get_save_data(self):
        buf = BytesIO()
        handler = rt.RichTextXMLHandler()
        handler.SetFlags(wx.richtext.RICHTEXT_HANDLER_INCLUDE_STYLESHEET | wx.richtext.RICHTEXT_TYPE_XML)
        handler.SaveFile(self.rich_text_control.GetBuffer(), buf)
        return buf

    def load_saved_buffer(self, buffer):
        print(buffer.getvalue().decode())

        def parse_buffer(_root):
            for element in _root:
                if element.tag.split("}")[-1] == "text":
                    self.rich_text_control.WriteText(str(element.text))
                if len(element) > 0:
                    parse_buffer(element)

        self.rich_text_control.Clear()
        root = ET.parse(StringIO(buffer.getvalue().decode()))
        root = root.getroot()
        parse_buffer(root)
        self.rich_text_control.Refresh()

    def on_event(self, e, *args):
        if e.GetId() == ID_ALIGN_CENTER:
            self.btn_align_center.select()
            self.buttons_panel.Refresh()

        e.Skip()

    def ForwardEvent(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rich_text_control.ProcessEvent(evt)
