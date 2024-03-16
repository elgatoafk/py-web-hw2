from abc import ABC, abstractmethod

class AbstractView(ABC):
    
    """Abstract base class for views.
    """    
    @abstractmethod
    def display_info(self, info):
        pass

class ConsoleView(AbstractView):
    """Class for console view"""
    def display_info(self, info: any) -> None:
        """Displays the provided information.


        :param info: The information to be displayed.
        :type info: any
        """        
        print(info)
    
class WebView(AbstractView):
    """Class for web view"""    
    def display_info(self, info: any):
        pass


class UserInterface:
    """Class for interacting with the user"""    
    def __init__(self, view) -> None:
        self.view = view
    
    def display_info(self, info:any):
        """Displays the provided information using the associated view object.


        :param info: The information to be displayed.
        :type info: any
        """        
        self.view.display_info(info)