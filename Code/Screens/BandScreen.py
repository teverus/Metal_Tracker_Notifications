from Code.TeverusSDK.Screen import Screen, ACTIONS_STUB, SCREEN_WIDTH, GO_BACK_ACTION
from Code.TeverusSDK.Table import Table


class BandScreen(Screen):
    def __init__(self, band_name):
        self.actions = [ACTIONS_STUB]

        self.table = Table(
            table_title=band_name, table_width=SCREEN_WIDTH, footer=[GO_BACK_ACTION]
        )

        super(BandScreen, self).__init__(self.table, self.actions)
