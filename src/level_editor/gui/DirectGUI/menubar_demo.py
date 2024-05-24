from menu import DropDownMenu


gameSlots={}
for s in range(4):
    gameSlots[s]=None


def create_game_menu_items():
    return (
    ('_New', 0, newGame),
    
    0, # separator
    
    ('_Load', 0, [('slot %s'%(s+1), 0, loadGame if gameSlots[s] else 0, s) for s in range(4)]),
    ('_Save', 0, [('slot %s'%(s+1), 0, saveGame, s) for s in range(4)]),
    
    0, # separator
    
    ('Prefe_rence', 0, lambda:0),
    
    0, # separator
    
    ('E_xit>Escape', 'lilsmiley.rgba', exit))


gameMenu = DropDownMenu(
    items=(('_Game', create_game_menu_items),
           ('_View', createViewMenuItems),
           ('Mo_del',createModelMenuItems),
           ('_Menu', createMenuMenuItems),
           ('_Help', createHelpMenuItems)),
           
    sidePad=.75,
    
    align=DropDownMenu.ALeft,
    #~ align=DropDownMenu.ACenter,
    #~ align=DropDownMenu.ARight,
    
    #~ effect=DropDownMenu.ESlide,
    effect=DropDownMenu.EStretch,
    #~ effect=DropDownMenu.EFade,
    
    edgePos=DropDownMenu.PTop,
    #~ edgePos=DropDownMenu.PBottom,
    #~ edgePos=DropDownMenu.PLeft,
    #~ edgePos=DropDownMenu.PRight,

    #~ font=loader.loadFont('fonts/Medrano.ttf'),
    baselineOffset=-.35,
    scale=.045, itemHeight=1.2, leftPad=.2,
    separatorHeight=.3,
    underscoreThickness=1,

    BGColor=(.9,.9,.8,.94),
    BGBorderColor=(.8,.3,0,1),
    separatorColor=(0,0,0,1),
    frameColorHover=(.3,.3,.3,1),
    frameColorPress=(0,1,0,.85),
    textColorReady=(0,0,0,1),
    textColorHover=(1,.7,.2,1),
    textColorPress=(0,0,0,1),
    textColorDisabled=(.65,.65,.65,1),
    draggable=True,
    onMove=menuBarMoved
 )

 