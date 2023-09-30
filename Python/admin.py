import os
import sys


def DoIt(fn1, fn2, fn3):
        f1 = open(fn1)
        f2 = open(fn2)
        f3 = open(fn3)

        lines = f1.readlines()

        lines = [s.replace("'#If DEBUG Then"                        , "#If DEBUG Then '!!"                          ) for s in lines]
        lines = [s.replace("'        txtServerName.Enabled = True"  , "        txtServerName.Enabled = True '!!"    ) for s in lines]
        lines = [s.replace("'        txtServerName.ReadOnly = False", "        txtServerName.ReadOnly = False '!!"  ) for s in lines]
        lines = [s.replace("'        txtDBName.Enabled = True"      , "        txtDBName.Enabled = True '!!"        ) for s in lines]
        lines = [s.replace("'        txtDBName.ReadOnly = False"    , "        txtDBName.ReadOnly = False '!!"      ) for s in lines]
        lines = [s.replace("'        txtUID.Text = \"admin\""       , "        txtUID.Text = \"admin\" '!!"         ) for s in lines]
        lines = [s.replace("'        txtPWD.Text = \"password\""    , "        txtPWD.Text = \"password\" '!!"      ) for s in lines]
        lines = [s.replace("'#End If"                               , "#End If '!!"                                 ) for s in lines]

        f1.close();
        f1 = open(fn1, "w")
        print ("Writing ", f1.name.replace("/", "\\"))
        f1.writelines(lines)
        f1.close();

        lines = f2.readlines()

        lines = [s.replace("'      If Text.Contains(\"Administration Permissions Management\") Then", "If Text.Contains(\"Administration Permissions Management\") Then '!!"    ) for s in lines]
        lines = [s.replace("'     txtUID.Text = \"AdminSecUser\""                                   , "    txtUID.Text = \"AdminSecUser\" '!!"                                  ) for s in lines]
        lines = [s.replace("'     Else"                                                             , "Else '!!"                                                                ) for s in lines]
        lines = [s.replace("'    txtUID.Text = \"admin\""                                           , "    txtUID.Text = \"admin\" '!!"                                         ) for s in lines]
        lines = [s.replace("'   End If"                                                             , "End If '!!"                                                              ) for s in lines]
        lines = [s.replace("'   txtPWD.Text = \"password\""                                         , "txtPWD.Text = \"password\" '!!"                                          ) for s in lines]

        f2.close()
        f2 = open(fn2, "w")
        print ("Writing ", f2.name.replace("/", "\\"))
        f2.writelines(lines)
        f2.close()

        lines = f3.readlines()

        lines = [s.replace("//txtUID.Text = \"admin\";"     , "txtUID.Text = \"admin\"; //!!"        ) for s in lines]
        lines = [s.replace("//txtPWD.Text = \"password\";"  , "txtPWD.Text = \"password\"; //!!"     ) for s in lines]

        f3.close()
        f3 = open(fn3, "w")
        print ("Writing ", f3.name.replace("/", "\\"))
        f3.writelines(lines)
        f3.close()

def UndoIt(fn1, fn2, fn3):
    f1 = open(fn1)
    f2 = open(fn2)
    f3 = open(fn3)

    lines = f1.readlines()

    lines = [s.replace("#If DEBUG Then '!!"                          , "'#If DEBUG Then"                        ) for s in lines]
    lines = [s.replace("        txtServerName.Enabled = True '!!"    , "'        txtServerName.Enabled = True"  ) for s in lines]
    lines = [s.replace("        txtServerName.ReadOnly = False '!!"  , "'        txtServerName.ReadOnly = False") for s in lines]
    lines = [s.replace("        txtDBName.Enabled = True '!!"        , "'        txtDBName.Enabled = True"      ) for s in lines]
    lines = [s.replace("        txtDBName.ReadOnly = False '!!"      , "'        txtDBName.ReadOnly = False"    ) for s in lines]
    lines = [s.replace("        txtUID.Text = \"admin\" '!!"         , "'        txtUID.Text = \"admin\""       ) for s in lines]
    lines = [s.replace("        txtPWD.Text = \"password\" '!!"      , "'        txtPWD.Text = \"password\""    ) for s in lines]
    lines = [s.replace("#End If '!!"                                 , "'#End If"                               ) for s in lines]

    f1.close();
    f1 = open(fn1, "w")
    print ("Reverting ", f1.name.replace("/", "\\"))
    f1.writelines(lines)
    f1.close();

    lines = f2.readlines()

    lines = [s.replace("If Text.Contains(\"Administration Permissions Management\") Then '!!", "'      If Text.Contains(\"Administration Permissions Management\") Then") for s in lines]
    lines = [s.replace("    txtUID.Text = \"AdminSecUser\" '!!"                              , "'     txtUID.Text = \"AdminSecUser\""                                   ) for s in lines]
    lines = [s.replace("Else '!!"                                                            , "'     Else"                                                             ) for s in lines]
    lines = [s.replace("    txtUID.Text = \"admin\" '!!"                                     , "'    txtUID.Text = \"admin\""                                           ) for s in lines]
    lines = [s.replace("End If '!!"                                                          , "'   End If"                                                             ) for s in lines]
    lines = [s.replace("txtPWD.Text = \"password\" '!!"                                      , "'   txtPWD.Text = \"password\""                                         ) for s in lines]

    f2.close()
    f2 = open(fn2, "w")
    print ("Reverting ", f2.name.replace("/", "\\"))
    f2.writelines(lines)
    f2.close()

    lines = f3.readlines()

    lines = [s.replace("txtUID.Text = \"admin\"; //!!"    , "//txtUID.Text = \"admin\";"     ) for s in lines]
    lines = [s.replace("txtPWD.Text = \"password\"; //!!" , "//txtPWD.Text = \"password\";"  ) for s in lines]

    f3.close()
    f3 = open(fn3, "w")
    print ("Reverting ", f3.name.replace("/", "\\"))
    f3.writelines(lines)
    f3.close()

for i in range (1, len(sys.argv)):
    if sys.argv[i] == "-u":
        UndoIt('C:/devroot/mainline/bw-main/BankWorld/Admin/BWDataBaseLogin/CfrmLoginDAL.vb',
            'C:/devroot/mainline/bw-main/BankWorld/Admin/BWDataBaseLogin20/cfrmLogin.vb',
            'C:/devroot/mainline/bw-main/BankWorldATM/Admin/ATMManager/DBLogin/CFrmLogin.cs')
        UndoIt('D:/devroot/554/bw-main/BankWorld/Admin/BWDataBaseLogin/CfrmLoginDAL.vb',
            'D:/devroot/554/bw-main/BankWorld/Admin/BWDataBaseLogin20/cfrmLogin.vb',
            'D:/devroot/554/bw-main/BankWorldATM/Admin/ATMManager/DBLogin/CFrmLogin.cs')        
        exit()

DoIt('C:/devroot/mainline/bw-main/BankWorld/Admin/BWDataBaseLogin/CfrmLoginDAL.vb',
     'C:/devroot/mainline/bw-main/BankWorld/Admin/BWDataBaseLogin20/cfrmLogin.vb',
     'C:/devroot/mainline/bw-main/BankWorldATM/Admin/ATMManager/DBLogin/CFrmLogin.cs')
DoIt('D:/devroot/554/bw-main/BankWorld/Admin/BWDataBaseLogin/CfrmLoginDAL.vb',
     'D:/devroot/554/bw-main/BankWorld/Admin/BWDataBaseLogin20/cfrmLogin.vb',
     'D:/devroot/554/bw-main/BankWorldATM/Admin/ATMManager/DBLogin/CFrmLogin.cs')


