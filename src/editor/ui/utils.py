from wx import ITEM_NORMAL, MenuItem


def build_menu(menu, items):
    for i in range(len(items)):
        _items = items[i]

        if _items == "":
            menu.AppendSeparator()
            continue
        
        menu_item = MenuItem(menu, _items[0], _items[1], kind=ITEM_NORMAL)
        menu.Append(menu_item)
