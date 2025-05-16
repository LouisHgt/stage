from PyQt5 import QtCore # type: ignore

class ChangeEventFilter(QtCore.QObject):
    def __init__(self, lib_bassin, formView):
        super().__init__()
        self.lib_bassin = lib_bassin
        self.formView = formView
        
    def eventFilter(self, watched, event):
        """
            Appelé quand un evenement survient sur un element du formulaire scenario
        """
        # Quand la souris rentre dans la zone
        if event.type() == QtCore.QEvent.Enter:
            # On highlight le bassin correspondant
            self.formView.highlightBassin(self.lib_bassin)
            return True
        elif event.type() == QtCore.QEvent.Leave:
            # On Cache le highlight
            # self.formView.highlightBassin()
            return True
        else:
            # Sinon on laisse gérer les evenemtns pas la classe parente
            return super().eventFilter(watched, event)