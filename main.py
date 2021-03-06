import os.path, sys, logging, copy
from code.userinterface import UserInterface
from code.factory import Factory
from code.export import Export
from code.messages import *
from code.menu import Menu
from code.suppliers.articles import *
from code.updater import Updater

export = Export()

def main():
    

    terminal = UserInterface()
    terminal.PrintTitle(TITLE_SOFTWARE)
    
    TryUpdateSoftware(terminal)

    menu = buildMenu()
    #the menu callbar creates the supplier feed object
    supplier = menu.openAndExecuteMenuOption()
    if not isinstance(supplier, Articles):
        PrintExeptionAndQuit(ERROR_SUPPLIER_BAD_INSTANCE_TYPE, None)
    
    try:       
        LogInit(supplier)

        terminal.PrintSection(TITLE_IMPORT_SUPPLIER_DATA)
        GetSupplierData(terminal, supplier)
           

        terminal.PrintSection(TITLE_EXPORT_STANDARD_FORMAT)
        export.ExportDataForOnlineshop(supplier, supplier.paths.getSupplierFeedExportFile())
        
        
        terminal.PrintSection(TITLE_REMOVE_IRRELEVANT_ARTICLES)
        supplier.RemoveIrrelevantArticles()
        PrintArticlesNumber(supplier)
        
        
        terminal.PrintSection(TITLE_IMPORT_SHOP_DATA)      
        shopData = Factory.CreateFeedObjectForShop()
        shopData.Import()
        shopData.FilterBySupplier(supplier.code)
        PrintArticlesNumber(shopData)

        
        terminal.PrintSection(TITLE_COMPARING_SHOP_AND_SUPPLIER_DATA)
        ProcessUpdatedArticles(shopData, supplier)
        newArticles = ProcessNewArticles(shopData, supplier)
        ProcessDeletedArticles(shopData, supplier)

        
        DownloadImagesIfUserWants(terminal, newArticles)
          
    except Exception as ex:
        PrintExeptionAndQuit(ERROR_MSG, ex)
        
    input(MSG_PRESS_ENTER_TO_QUIT)


def PrintArticlesNumber(articlesObject):
    print(MSG_NUMBER_OF_ARTICLES + str(articlesObject.ArticlesCount()))


def TryUpdateSoftware(terminal):    
    updater = Updater(gitUrl='https://github.com/AdrianMos/feed-importer.git',
                      gitBranch='master',
                      softwarePath = os.getcwd())

    print(MSG_SOFTWARE_VERSION.upper()
          + updater.GetCurrentSoftwareVersion() + '\n')

    terminal.PrintSeparator()
    print(TITLE_SOFTWARE_UPDATE)
    
    try :
        updater.Download()
        if updater.IsUpdateRequired():
            print(updater.GetSoftwareUpdateMessage())
            if terminal.AskYesOrNo(QUESTION_UPDATE_SOFTWARE) == YES:
                updater.Install()
        else:
            print(MSG_NO_NEW_SOFTWARE)
            
    except Exception as ex:
        print(MSG_SOFTWARE_UPDATE_FAILED)


def GetSupplierData(terminal, supplier):
    if terminal.AskYesOrNo(QUESTION_DOWNLOAD_FEED) == YES:
        supplier.DownloadFeed()       
        
    numErrors = supplier.Import()
    if numErrors > 0:
        print(MSG_FEED_ERRORS + str(numErrors))
        
    supplier.ConvertToOurFormat()
    PrintArticlesNumber(supplier)
    
    AskUserConfirmationToContinueIfPossibleErrorIsDetected(terminal, supplier)


def AskUserConfirmationToContinueIfPossibleErrorIsDetected(terminal, supplier):
    if supplier.ArticlesCount() < 50:            
        if terminal.AskYesOrNo(MSG_WARNING_LESS_50_ARTICLES + QUESTION_CONTINUE) == NO:
            PrintExeptionAndQuit(MSG_USER_SELECTION_QUIT, None)


def DownloadImagesIfUserWants(terminal, articles):
    terminal.PrintSection(TITLE_DOWNLOAD_NEW_IMAGES)

    askUserMessage = QUESTION_DOWNLOAD_IMAGES_FOR_NEW_ARTICLES \
                     + ' (' + str(articles.ArticlesCount()) + ')'
                     
    if terminal.AskYesOrNo(askUserMessage) == YES:
            articles.DownloadImages();
          
  
def ProcessUpdatedArticles (shopData, supplier):
    print(SUBTITLE_UPDATED_ARTICLES)
    supplierCopy = copy.deepcopy(supplier)
    supplierCopy.IntersectWith(shopData)
    supplierCopy.RemoveArticlesWithNoUpdatesComparedToReference(reference=shopData)

    messagesList = supplierCopy.GetComparisonHumanReadableMessages(reference=shopData)

    PrintArticlesNumber(supplierCopy)
    export.ExportPriceAndAvailabilityAndMessages(supplierCopy, 
                                                 messagesList, 
                                                 supplier.paths.getUpdatedArticlesFile())
    
    
def ProcessDeletedArticles (shopData, supplier):
    print(SUBTITLE_DELETED_ARTICLES)
    articlesToDelete = copy.deepcopy(shopData)
    articlesToDelete.RemoveArticles(supplier)
       
    PrintArticlesNumber(articlesToDelete)
    export.ExportArticlesForDeletion(articlesToDelete,
                                     supplier.paths.getDeletedArticlesFile())
    

def ProcessNewArticles (shopData, supplier):
    print(SUBTITLE_NEW_ARTICLES)
    newArticles = copy.deepcopy(supplier)
    newArticles.RemoveArticles(shopData)
    newArticles.RemoveInactiveArticles()

    PrintArticlesNumber(newArticles)
    export.ExportAllData(newArticles,  supplier.paths.getNewArticlesFile())
    return newArticles

    
def LogInit(supplier): 
    logging.basicConfig(filename = supplier.paths.getLogFile(),
                        level = logging.INFO, 
                        filemode = 'w',
                        format ='%(asctime)s     %(message)s')


def exitApplication(data):
    print("... bye")
    sys.exit(0)


def buildMenu():
    menu = Menu(title = "Optiuni disponibile:",
                       userMessage = 'Alegeti:')
    
    menu.addMenuItem(name="Iesire",
                     callback=exitApplication,
                     arguments="")

    #format: display_text, invoked_supplier_class
    items = [["Actualizare Nancy (NAN)",        "ArticlesNancy"],
             ["Actualizare BebeBrands (HBBA)",  "ArticlesBebeBrands"],
             ["Actualizare Hubners (HHUB)",     "ArticlesHubners"],
             ["Actualizare BabyDreams (HDRE)",  "ArticlesBabyDreams"],
             ["Actualizare Bebex (BEB)",        "ArticlesBebex"],
             ["Actualizare BabyShops (HMER)",   "ArticlesBabyShops"]
             #,["  NU Actualizare KidsDecor (HDEC)",      "ArticlesKidsDecor"]
             ]

    for item in items:
        menu.addMenuItem(name = item[0],
                         callback = Factory.CreateSupplierFeedObject,
                         arguments = item[1])
        
    return menu

                        
if __name__ == '__main__':
    main()
