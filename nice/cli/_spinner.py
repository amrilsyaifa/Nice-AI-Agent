import random
import threading
import time
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()

THINKING_MESSAGES = [
    # Indonesia
    "Berpikir...", "Menyusun jawaban...", "Sebentar ya...", "Memproses...", "Hampir selesai...",
    # English
    "Thinking...", "Preparing response...", "Just a moment...", "Processing...", "Almost done...",
    # Japanese
    "考えています...", "回答を準備しています...", "少々お待ちください...", "処理中です...", "もうすぐ完了します...",
    # Korean
    "생각 중입니다...", "답변을 준비 중입니다...", "잠시만 기다려주세요...", "처리 중입니다...", "거의 완료되었습니다...",
    # Chinese
    "正在思考...", "正在整理回答...", "请稍等...", "处理中...", "即将完成...",
    # Arabic
    "جارٍ التفكير...", "جارٍ تجهيز الرد...", "لحظة من فضلك...", "جارٍ المعالجة...", "اكتمل تقريبًا...",
    # French
    "Je réfléchis...", "Préparation de la réponse...", "Un instant...", "Traitement en cours...", "Presque terminé...",
    # German
    "Ich denke nach...", "Antwort wird vorbereitet...", "Einen Moment bitte...", "Wird verarbeitet...", "Fast fertig...",
    # Spanish
    "Pensando...", "Preparando respuesta...", "Un momento...", "Procesando...", "Casi terminado...",
    # Portuguese
    "Pensando...", "Preparando resposta...", "Só um momento...", "Processando...", "Quase pronto...",
    # Russian
    "Думаю...", "Готовлю ответ...", "Секундочку...", "Обработка...", "Почти готово...",
    # Hindi
    "सोच रहा हूँ...", "उत्तर तैयार कर रहा हूँ...", "एक क्षण...", "प्रोसेस किया जा रहा है...", "लगभग पूरा हो गया...",
    # Thai
    "กำลังคิด...", "กำลังเตรียมคำตอบ...", "รอสักครู่...", "กำลังประมวลผล...", "ใกล้เสร็จแล้ว...",
    # Vietnamese
    "Đang suy nghĩ...", "Đang chuẩn bị câu trả lời...", "Chờ một chút nhé...", "Đang xử lý...", "Sắp xong rồi...",
    # Turkish
    "Düşünüyorum...", "Yanıt hazırlanıyor...", "Bir saniye lütfen...", "İşleniyor...", "Neredeyse hazır...",
    # Sunda
    "Nuju mikir...", "Nyusun jawaban...", "Sakedap nya...", "Nuju diprosés...", "Ampir réngsé...",
    # Jawa
    "Lagi mikir...", "Nyusun jawaban...", "Enteni sedhela...", "Lagi diproses...", "Meh rampung...",
    # Batak
    "Dang marpikkir...", "Mangulahon jawaban...", "Santabi jolo...", "Diproses dope...", "Nunga hampir salese...",
    # Minang
    "Lagi bapikia...", "Manyusun jawaban...", "Tunggu sabanta...", "Lagi diproses...", "Hampia salasa...",
    # Bali
    "Sedek mikir...", "Nyusun jawaban...", "Antos sebentar...", "Sedek diproses...", "Sampun wantah...",
]


def run_with_spinner(fn) -> tuple:
    """Jalankan fn di background thread dengan spinner. Return (result, error)."""
    result = [None]
    error = [None]

    def worker():
        try:
            result[0] = fn()
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    try:
        with console.status(f"[dim]{random.choice(THINKING_MESSAGES)}[/dim]", spinner="dots") as status:
            while thread.is_alive():
                time.sleep(2)
                if thread.is_alive():
                    status.update(f"[dim]{random.choice(THINKING_MESSAGES)}[/dim]")
            thread.join()
    except KeyboardInterrupt:
        return None, KeyboardInterrupt("Dibatalkan.")

    return result[0], error[0]


def stream_quiet(provider, messages: list, tools: list = None) -> tuple[str, Exception | None]:
    """Stream response as plain text — no decorations, suitable for scripting."""
    full = ""
    try:
        for chunk in provider.chat_stream(messages, tools=tools):
            print(chunk, end="", flush=True)
            full += chunk
        print()
        return full, None
    except KeyboardInterrupt:
        return full, KeyboardInterrupt("Cancelled.")
    except Exception as e:
        return full, e


def stream_markdown(provider, messages: list, tools: list = None) -> tuple[str, Exception | None]:
    """
    Stream provider response with live Markdown rendering.
    Shows a spinner until the first token arrives, then renders tokens
    in-place as Markdown. Returns (full_response, error_or_None).
    """
    console.print("[bold]AI[/bold]")
    full_response = ""

    try:
        gen = provider.chat_stream(messages, tools=tools)

        # Show spinner while waiting for first token
        first_chunk = None
        with console.status(
            f"[dim]{random.choice(THINKING_MESSAGES)}[/dim]", spinner="dots"
        ) as status:
            while first_chunk is None:
                try:
                    first_chunk = next(gen)
                except StopIteration:
                    return "", None
                if first_chunk == "":
                    # Empty chunk — keep spinner, try next
                    status.update(f"[dim]{random.choice(THINKING_MESSAGES)}[/dim]")
                    first_chunk = None

        # First token arrived — render progressively
        full_response = first_chunk
        with Live(
            Markdown(full_response),
            console=console,
            refresh_per_second=15,
            vertical_overflow="visible",
        ) as live:
            for chunk in gen:
                full_response += chunk
                live.update(Markdown(full_response))

        return full_response, None
    except KeyboardInterrupt:
        return full_response, KeyboardInterrupt("Cancelled.")
    except Exception as e:
        return full_response, e
