import wx


def build_menu(menu, items):
    for i in range(len(items)):
        _items = items[i]

        if _items == "":
            menu.AppendSeparator()
            continue

        menu_item = wx.MenuItem(menu, _items[0], _items[1])
        # menu_item.SetBitmap(wx.Bitmap('exit.png'))
        menu.Append(menu_item)
