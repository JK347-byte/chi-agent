import os
import logging
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CallbackQueryHandler,
    MessageHandler, CommandHandler, filters, ContextTypes,
)
from sheets_client import SheetsClient, STATUS_ACTIVE, STATUS_NOSHOW, STATUS_PAUSED
from logic import (
    suggest_next_date, quota_warning,
    year_window, visits_in_window, get_rules,
)
from config import DAILY_REMINDER_HOUR, DAILY_REMINDER_MINUTE

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN      = os.getenv("CARE_BOT_TOKEN")
GROUP_ID   = int(os.getenv("CARE_GROUP_CHAT_ID"))
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SHEET_NAME = os.getenv("SPREADSHEET_NAME", "照護追蹤系統")

sheets = SheetsClient(CREDS_FILE, SHEET_NAME)


# ── 訊息格式 ──────────────────────────────────────────────

def patient_card(p: dict, visits: list[date]) -> str:
    rules = get_rules(p["project"])
    today = date.today()
    quota = rules.get("max_visits_per_year", 3)

    last     = p["last_visit"].strftime("%Y-%m-%d") if p["last_visit"] else "尚未回診"
    interval = f"{p['tracking_interval']} 天" if p["tracking_interval"] else "未設定"
    nxt      = p["earliest_next"].strftime("%Y-%m-%d") if p["earliest_next"] else "—"

    if p["enrollment_date"]:
        w_start, w_end = year_window(p["enrollment_date"], today)
        used = len(visits_in_window(visits, w_start, w_end))
        icon = "🟢" if quota - used > 1 else ("🟡" if quota - used == 1 else "🔴")
        quota_line = f"{icon} 本年度：{used}/{quota} 次（年度至 {w_end.strftime('%Y-%m-%d')}）"
    else:
        quota_line = "⚠️ 收案日期未填，無法計算年度額度"

    return (
        f"👤 {p['name']}（{p['medical_id']}）\n"
        f"🏥 {p['project']}\n"
        f"📅 最近回診：{last}\n"
        f"⏱ 追蹤間隔：{interval}\n"
        f"📆 下次預計：{nxt}\n"
        f"{quota_line}"
    )


def keyboard_visited(mid: str, proj: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 已回診", callback_data=f"visited|{mid}|{proj}"),
        InlineKeyboardButton("⏸ 暫停追蹤", callback_data=f"pause|{mid}|{proj}"),
    ]])


def keyboard_set_interval(mid: str, proj: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ 設定追蹤間隔", callback_data=f"interval|{mid}|{proj}")],
        [InlineKeyboardButton("⏸ 暫停追蹤",     callback_data=f"pause|{mid}|{proj}")],
    ])


# ── 排程任務 ──────────────────────────────────────────────

async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    today = date.today()
    patients = sheets.all_patients()

    reminder_list, overdue_list, warn_list = [], [], []

    for p in patients:
        if p["status"] not in (STATUS_ACTIVE, STATUS_NOSHOW):
            continue

        visits = sheets.patient_visits(p["medical_id"], p["project"])

        if p["earliest_next"]:
            if p["earliest_next"] == today:
                reminder_list.append((p, visits))
            elif p["earliest_next"] < today:
                # 逾期：最近回診日早於預定日，表示未回診
                if not p["last_visit"] or p["last_visit"] < p["earliest_next"]:
                    overdue_list.append(p)

        if p["enrollment_date"] and quota_warning(p["enrollment_date"], visits, p["project"]):
            warn_list.append((p, visits))

    # 今日預計回診
    if reminder_list:
        await context.bot.send_message(GROUP_ID,
            f"🔔 *今日預計回診* — {today.strftime('%Y-%m-%d')}", parse_mode="Markdown")
        for p, visits in reminder_list:
            await context.bot.send_message(GROUP_ID, patient_card(p, visits),
                reply_markup=keyboard_visited(p["medical_id"], p["project"]))

    # 逾期未回診
    if overdue_list:
        lines = [f"⚠️ *逾期未回診* — 以下個案已超過追蹤日\n"]
        for p in overdue_list:
            nxt = p["earliest_next"].strftime("%Y-%m-%d") if p["earliest_next"] else "—"
            days_late = (today - p["earliest_next"]).days if p["earliest_next"] else 0
            lines.append(
                f"• {p['name']}（{p['medical_id']}）｜{p['project']}\n"
                f"  預定：{nxt}｜已逾 {days_late} 天"
            )
        await context.bot.send_message(GROUP_ID, "\n".join(lines), parse_mode="Markdown")

    # 年度額度警告
    if warn_list:
        lines = ["⚠️ *年度額度警告* — 年度即將結束且尚有剩餘申報次數\n"]
        for p, visits in warn_list:
            rules = get_rules(p["project"])
            w_start, w_end = year_window(p["enrollment_date"], today)
            used = len(visits_in_window(visits, w_start, w_end))
            remaining = rules.get("max_visits_per_year", 3) - used
            days_left = (w_end - today).days
            lines.append(
                f"• {p['name']}（{p['medical_id']}）｜{p['project']}\n"
                f"  剩餘 {remaining} 次，年度於 {days_left} 天後結束（{w_end.strftime('%Y-%m-%d')}）"
            )
        await context.bot.send_message(GROUP_ID, "\n".join(lines), parse_mode="Markdown")


# ── 按鈕處理 ──────────────────────────────────────────────

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts  = query.data.split("|")
    action = parts[0]
    mid    = parts[1]
    proj   = parts[2]
    by     = update.effective_user.first_name or "診所人員"
    today  = date.today()

    patients = sheets.all_patients()
    p = next((x for x in patients if x["medical_id"] == mid and x["project"] == proj), None)
    if not p:
        await query.edit_message_text("找不到個案，請確認病歷號。")
        return

    visits = sheets.patient_visits(mid, proj)

    if action == "visited":
        sheets.add_visit(mid, p["name"], proj, today, recorded_by=by)
        sheets.update_patient(p["row"], {"last_visit": today, "status": STATUS_ACTIVE}, updated_by=by)

        rules = get_rules(proj)
        is_first = len(visits) == 0
        suggested_days = rules.get("first_interval_days", 70) if is_first else rules.get("subsequent_interval_days", 70)

        context.chat_data["awaiting_interval"] = {
            "medical_id": mid, "project": proj,
            "patient_row": p["row"], "name": p["name"],
            "last_visit": today, "suggested_days": suggested_days,
        }

        await query.edit_message_text(
            f"✅ 已記錄回診（{today.strftime('%Y-%m-%d')}）\n\n"
            f"請設定 {p['name']} 的下次追蹤間隔\n"
            f"建議：{suggested_days} 天\n\n"
            f"直接在對話框輸入天數，或點下方使用建議值",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"✅ 使用建議值（{suggested_days} 天）",
                    callback_data=f"setinterval|{mid}|{proj}|{suggested_days}",
                )
            ]])
        )

    elif action == "interval":
        # 手動進入設定追蹤間隔（從可安排回診觸發）
        rules = get_rules(proj)
        is_first = len(visits) == 0
        default_days = rules.get("first_interval_days", 70) if is_first else rules.get("subsequent_interval_days", 70)
        hint = p["tracking_interval"] or default_days

        context.chat_data["awaiting_interval"] = {
            "medical_id": mid, "project": proj,
            "patient_row": p["row"], "name": p["name"],
            "last_visit": p["last_visit"], "suggested_days": hint,
        }

        last_str = p["last_visit"].strftime("%Y-%m-%d") if p["last_visit"] else "尚未回診"
        await query.edit_message_text(
            f"⏱ 設定追蹤間隔｜{p['name']}（{mid}）\n"
            f"最近回診：{last_str}\n\n"
            f"請輸入追蹤間隔天數（建議：{hint} 天）\n"
            f"或點下方使用建議值，輸入「取消」放棄",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"✅ 使用 {hint} 天",
                    callback_data=f"setinterval|{mid}|{proj}|{hint}",
                )
            ]])
        )

    elif action == "setinterval":
        interval_days = int(parts[3])
        last_visit = p["last_visit"]
        if not last_visit:
            await query.edit_message_text("尚未有回診記錄，無法計算下次日期。")
            return
        next_date = last_visit + timedelta(days=interval_days)
        sheets.update_patient(p["row"], {
            "tracking_interval": str(interval_days),
        }, updated_by=by)
        context.chat_data.pop("awaiting_interval", None)
        await query.edit_message_text(
            f"📅 已設定追蹤間隔\n{p['name']}（{mid}）｜{proj}\n"
            f"追蹤間隔：{interval_days} 天\n"
            f"下次預計回診：{next_date.strftime('%Y-%m-%d')}"
        )

    elif action == "pause":
        sheets.update_patient(p["row"], {"status": STATUS_PAUSED}, updated_by=by)
        await query.edit_message_text(f"⏸ 已暫停追蹤｜{p['name']}（{mid}）")


# ── 文字訊息處理 ──────────────────────────────────────────

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    by   = update.effective_user.first_name or "診所人員"

    # ① 等待輸入追蹤間隔
    pending = context.chat_data.get("awaiting_interval")
    if pending:
        if text == "取消":
            context.chat_data.pop("awaiting_interval", None)
            await update.message.reply_text("已取消。")
            return
        try:
            days = int(text)
            if days < 1:
                raise ValueError
        except ValueError:
            await update.message.reply_text("請輸入正整數天數，例如：70")
            return

        last_visit = pending.get("last_visit")
        if isinstance(last_visit, str):
            last_visit = date.fromisoformat(last_visit)
        if not last_visit:
            await update.message.reply_text("找不到最近回診日，請聯繫管理員。")
            return

        next_date = last_visit + timedelta(days=days)
        sheets.update_patient(pending["patient_row"], {
            "tracking_interval": str(days),
        }, updated_by=by)
        context.chat_data.pop("awaiting_interval", None)
        await update.message.reply_text(
            f"✅ 已設定\n{pending['name']}（{pending['medical_id']}）｜{pending['project']}\n"
            f"追蹤間隔：{days} 天\n"
            f"下次預計回診：{next_date.strftime('%Y-%m-%d')}"
        )
        return

    # ② 手動設定間隔指令：設定間隔 病歷號 專案 天數
    if text.startswith("設定間隔"):
        parts = text.split()
        if len(parts) < 4:
            await update.message.reply_text("格式：設定間隔 病歷號 專案 天數\n例：設定間隔 A123456789 代謝症候群 70")
            return
        mid, proj, days_str = parts[1], parts[2], parts[3]
        try:
            days = int(days_str)
        except ValueError:
            await update.message.reply_text("天數格式錯誤，請輸入數字")
            return
        patients = sheets.all_patients()
        p = next((x for x in patients if x["medical_id"] == mid and x["project"] == proj), None)
        if not p:
            await update.message.reply_text(f"找不到個案：{mid}｜{proj}")
            return
        if not p["last_visit"]:
            await update.message.reply_text("尚未有回診記錄，無法計算下次日期")
            return
        next_date = p["last_visit"] + timedelta(days=days)
        sheets.update_patient(p["row"], {
            "tracking_interval": str(days),
        }, updated_by=by)
        await update.message.reply_text(
            f"✅ 已設定\n{p['name']}（{mid}）｜{proj}\n"
            f"追蹤間隔：{days} 天\n"
            f"下次預計回診：{next_date.strftime('%Y-%m-%d')}"
        )


# ── 指令處理 ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 照護追蹤系統已啟動\n\n"
        "指令：\n"
        "/test — 立即觸發今日提醒（測試用）\n"
        "/status — 顯示目前追蹤中個案數\n\n"
        "手動設定：設定間隔 病歷號 專案 天數"
    )


async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ 正在執行每日檢查...")
    await daily_job(context)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    patients = sheets.all_patients()
    active = sum(1 for p in patients if p["status"] == STATUS_ACTIVE)
    noshow = sum(1 for p in patients if p["status"] == STATUS_NOSHOW)
    paused = sum(1 for p in patients if p["status"] == STATUS_PAUSED)
    await update.message.reply_text(
        f"📊 個案狀態總覽\n\n"
        f"🟢 追蹤中：{active} 人\n"
        f"⚠️ 逾期未回診：{noshow} 人\n"
        f"⏸ 暫停追蹤：{paused} 人\n"
        f"📋 合計：{len(patients)} 人"
    )


# ── 主程式 ────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("test",   cmd_test))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    jq = app.job_queue
    from datetime import time as dtime
    jq.run_daily(daily_job,
                 time=dtime(DAILY_REMINDER_HOUR, DAILY_REMINDER_MINUTE),
                 name="daily")

    print("✅ 照護追蹤 Bot 啟動中...")
    app.run_polling(allowed_updates=["message", "callback_query", "chat_member"])


if __name__ == "__main__":
    main()
