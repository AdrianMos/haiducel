from code.messages import *

class UserInterface(object):
    
    TITLE_LENGTH = 79
    FILL_CHARACTER = '-'
    HORIZONTAL_LINE = FILL_CHARACTER * TITLE_LENGTH + '\n'
    
    titleCounter = 1;
    
    def MainTitle(self, title):
        
        separator = '\n' + '*' * self.TITLE_LENGTH
        print(separator + '\n')
        print(title.center(self.TITLE_LENGTH ,' ')) 
        print(separator)
        
    
    def Title(self, title):
        
        titleCountStr = '(' + str(self.titleCounter) + ')'
        
        if len(title) <= self.TITLE_LENGTH - 2:
            formatedTitle = title.upper().center(self.TITLE_LENGTH \
                                                 - len(titleCountStr),
                                                 self.FILL_CHARACTER)
            print('\n' + titleCountStr + formatedTitle + '\n')
        else:
            print(self.HORIZONTAL_LINE +
                  titleCountStr + ' ' +
                  title.upper() + '\n' +
                  self.HORIZONTAL_LINE)
        
        self.titleCounter += 1
    
    def HorizontalLine(self):
        print (self.HORIZONTAL_LINE)
    
    def AskYesOrNo(self, question):
        userInput=""
        print('')
        while (userInput!=YES and userInput!=NO):
            userInput = input(question + ' ' + YES + '/' + NO + ': >> ').lower()
        return userInput
    
    def AskInput(self, question):
        return input(question)

