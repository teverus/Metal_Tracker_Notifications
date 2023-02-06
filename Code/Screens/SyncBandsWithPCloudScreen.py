from Code.TeverusSDK.Screen import (
    Screen,
    Action,
    do_nothing,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
)
from Code.TeverusSDK.Table import Table


class SyncBandsWithPCloudScreen(Screen):
    def __init__(self):
        self.actions = [Action(function=do_nothing)]

        self.table = Table(
            table_title="Sync tracked bands with pCloud",
            table_width=SCREEN_WIDTH,
            footer=[GO_BACK_ACTION],
        )

        super(SyncBandsWithPCloudScreen, self).__init__(self.table, self.actions)
