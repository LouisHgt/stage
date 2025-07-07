from PyQt5.QtCore import QObject, QEvent # type: ignore

class WheelEventFilter(QObject):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._canvas = canvas

    def eventFilter(self, watched, event):
        # Vérifier si l'événement est un événement de molette (Wheel)
        # Et si l'objet surveillé (watched) est bien le viewport du canvas
        if event.type() == QEvent.Type.Wheel and watched == self._canvas.viewport():
            # Si c'est un événement de molette sur le viewport,
            # on retourne True pour indiquer qu'on a géré l'événement
            # et qu'il ne doit pas être traité davantage (donc, pas de zoom).
            return True
        else:
            # Pour tous les autres événements, on laisse le traitement standard se faire.
            # Il est crucial d'appeler la méthode eventFilter de la classe parente.
            return super().eventFilter(watched, event)