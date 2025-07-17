from aiogram.fsm.state import StatesGroup, State

class AddTransactionState(StatesGroup):
    ChoosingType = State()
    EnteringAmount = State()
    ChoosingPeriod = State()
    EnteringDescription = State()
    ChoosingCategory = State()

class ReportState(StatesGroup):
    ChoosingPeriod = State()

class UpdateState(StatesGroup):
    EnteringID = State()
    EnteringNewAmount = State()

class DeleteState(StatesGroup):
    EnteringID = State()