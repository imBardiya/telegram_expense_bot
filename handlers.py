from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database import add_transaction, get_transactions, delete_transaction, update_transaction
from states import AddTransactionState, ReportState, UpdateState, DeleteState
from exporter import export_transactions_csv
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


router = Router()

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ ثبت درآمد"), KeyboardButton(text="➖ ثبت هزینه")],
    [KeyboardButton(text="📊 گزارش"), KeyboardButton(text="✏️ ویرایش"), KeyboardButton(text="🗑️ حذف")],
], resize_keyboard=True)

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("سلام! یکی از گزینه‌ها رو انتخاب کن:", reply_markup=main_menu)

# ثبت درآمد یا هزینه
@router.message(F.text.in_(["➕ ثبت درآمد", "➖ ثبت هزینه"]))
async def start_transaction(message: Message, state: FSMContext):
    await state.set_state(AddTransactionState.EnteringAmount)
    t_type = "income" if "درآمد" in message.text else "expense"
    await state.update_data(t_type=t_type)
    await message.answer("مقدار رو وارد کن (مثلاً ۵۰۰):")

@router.message(AddTransactionState.EnteringAmount)
async def enter_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace("٫", ".").replace(",", ""))
        await state.update_data(amount=amount)
        await state.set_state(AddTransactionState.ChoosingPeriod)
        await message.answer("نوع دوره رو انتخاب کن:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="روزانه")], [KeyboardButton(text="هفتگی")], [KeyboardButton(text="ماهانه")]],
            resize_keyboard=True))
    except:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کن.")

@router.message(AddTransactionState.ChoosingCategory)
async def choose_category(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(category=category)
    await message.answer("توضیح اختیاری وارد کن (یا بزن ندارم):")
    await state.set_state(AddTransactionState.EnteringDescription)

@router.message(AddTransactionState.ChoosingPeriod)
async def choose_period(message: Message, state: FSMContext):
    period = message.text.strip()
    if period not in ["روزانه", "هفتگی", "ماهانه"]:
        await message.answer("لطفاً یکی از گزینه‌های دوره رو انتخاب کن.")
        return
    
    await state.update_data(period=period)
    await state.set_state(AddTransactionState.ChoosingCategory)
    await message.answer("دسته‌بندی رو وارد کن (مثلاً: غذا، حمل‌ونقل، حقوق):")

@router.message(AddTransactionState.EnteringDescription)
async def enter_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    description = message.text if message.text != "ندارم" else ""
    category = data.get('category', 'بدون دسته بندی')
    add_transaction(message.from_user.id, data["t_type"], data["amount"], data["period"], category, description)
    await state.clear()
    await message.answer("✅ تراکنش ذخیره شد.", reply_markup=main_menu)

# گزارش
@router.message(F.text == "📊 گزارش")
async def ask_report_period(message: Message, state: FSMContext):
    await state.set_state(ReportState.ChoosingPeriod)
    await state.update_data(period=message.text.strip())
    await message.answer("برای کدام دوره؟", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="روزانه")], [KeyboardButton(text="هفتگی")], [KeyboardButton(text="ماهانه")]],
        resize_keyboard=True))
    
@router.message(ReportState.ChoosingPeriod)
async def show_report(message: Message, state: FSMContext):
    requested_period = message.text.strip()
    txns = get_transactions(message.from_user.id)

    income = 0
    expense = 0
    details = []
    conversion_factor = {
    ("روزانه", "روزانه"): 1,
    ("روزانه", "هفتگی"): 7,
    ("روزانه", "ماهانه"): 30,
    ("هفتگی", "روزانه"): 1 / 7,
    ("هفتگی", "هفتگی"): 1,
    ("هفتگی", "ماهانه"): 4.3,  # چون ۴.۳ هفته در ماه داریم
    ("ماهانه", "روزانه"): 1 / 30,
    ("ماهانه", "هفتگی"): 1 / 4.3,
    ("ماهانه", "ماهانه"): 1,
}

    for txn_id, t_type, amount, period, description, category in txns:
        amount = float(amount)
        factor = conversion_factor.get((period, requested_period), 0)
        normalized_amount = amount * factor

        if t_type == "income":
            income += normalized_amount
        elif t_type == "expense":
            expense += normalized_amount
        details.append(f"\n🆔 {txn_id} 🔹 {'➕' if t_type == 'income' else '➖'}{category}:{normalized_amount:.0f} تومان \n{description}")
        
    balance = income - expense

    report_text = (
        f"📊 گزارش {requested_period}:\n"
        f"➕ درآمد: {income:.0f} تومان\n"
        f"➖ هزینه: {expense:.0f} تومان\n"
        f"💰 مانده: {balance:.0f} تومان"
    )

    report_text += '\n'.join(details)

    await message.answer(report_text)
    await state.clear()

# حذف
@router.message(F.text == "🗑️ حذف")
async def delete_start(message: Message, state: FSMContext):
    await state.set_state(DeleteState.EnteringID)
    await message.answer("شناسه تراکنش رو وارد کن که می‌خوای حذف بشه:")

@router.message(DeleteState.EnteringID)
async def delete_transaction_handler(message: Message, state: FSMContext):
    try:
        tid = int(message.text)
        delete_transaction(tid, message.from_user.id)
        await message.answer("✅ حذف شد.", reply_markup=main_menu)
        await state.clear()
    except:
        await message.answer("❌ شناسه نامعتبره.")

# ویرایش
@router.message(F.text == "✏️ ویرایش")
async def update_start(message: Message, state: FSMContext):
    await state.set_state(UpdateState.EnteringID)
    await message.answer("شناسه تراکنش رو بفرست که می‌خوای ویرایشش کنی:")

@router.message(UpdateState.EnteringID)
async def update_amount(message: Message, state: FSMContext):
    await state.update_data(transaction_id=int(message.text))
    await state.set_state(UpdateState.EnteringNewAmount)
    await message.answer("مقدار جدید رو وارد کن:")

@router.message(UpdateState.EnteringNewAmount)
async def do_update(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        new_amount = float(message.text)
        update_transaction(data["transaction_id"], new_amount)
        await message.answer("✅ ویرایش انجام شد.", reply_markup=main_menu)
        await state.clear()
    except:
        await message.answer("❌ عدد نامعتبر.")

@router.message(lambda msg: msg.text == "📤 خروجی گرفتن")
async def handle_export_button(message: Message, bot: Bot):
    await export_transactions_csv(message.from_user.id, message, bot)


@router.message(Command("export"))
async def handle_export_command(message: Message, bot: Bot):
    await export_transactions_csv(message.from_user.id, message, bot)

# فرضا این تابع هندل کننده دریافت دسته‌بندیه
@router.message(AddTransactionState.ChoosingCategory)
async def enter_category(message: Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)  # ذخیره مقدار دسته‌بندی در state
    await message.answer("حالا لطفاً توضیحات را وارد کن (اختیاری):")
    await AddTransactionState.next()  # یا هر state بعدی که داری

# مرحله بعد، دریافت توضیح و ثبت نهایی
@router.message(AddTransactionState.EnteringDescription)
async def enter_description(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    # اینجا حتما category رو هم داری
    category = data.get("category", "بدون دسته‌بندی")

    # سایر داده‌ها مثل amount، t_type، period رو هم از data بگیر
    amount = data.get("amount")
    t_type = data.get("t_type")
    period = data.get("period")

    # حالا صدا بزن add_transaction با همه پارامترها
    add_transaction(
        user_id=message.from_user.id,
        t_type=t_type,
        amount=amount,
        period=period,
        category=category,
        description=description
    )
    await message.answer("✅ تراکنش شما ثبت شد.")
    await state.clear()
