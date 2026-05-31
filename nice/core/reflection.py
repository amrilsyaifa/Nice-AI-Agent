

from nice.providers.registry import get_active_provider
from nice.tools.registry import execute_tool, TOOL_DEFINITIONS


MAX_RETRY = 3

REFLECTION_PROMPT = """Kamu adalah AI engineer yang sedang debug error.

Kamu punya tools: read_file, write_file, run_command, list_directory.

Workflow kamu:
1. Baca error yang terjadi
2. Baca file yang bermasalah
3. Analisis penyebab error
4. Fix file tersebut
5. Jalankan ulang untuk verifikasi

Selalu jawab dalam Bahasa Indonesia."""

def run_with_reflection(command: str, context_file: str = None) -> dict:
    """
    Jalankan command, kalau error — refleksi dan fix otomatis.
    Return dict dengan keys: success, output, attempts
    """

    provider = get_active_provider()
    attempts = []
   
    for attempt in range(1, MAX_RETRY + 1):
        print(f"\n{'='*50}")
        print(f"⚡ Attempt {attempt}/{MAX_RETRY}: {command}")
        print('='*50)

        # Jalankan command
        result = execute_tool("run_command", {"command": command})
        attempts.append({"attempt": attempt, "output": result})
       
        # Cek apakah berhasil
        is_error = (
            "error" in result.lower() or
            "traceback" in result.lower() or
            "exception" in result.lower() or
            "stderr" in result.lower()
        )

        if not is_error:
            print(f"✅ Berhasil di attempt {attempt}!")
            return {"success": True, "output": result, "attempts": attempts}
        
        # Ada error — minta LLM untuk fix
        print("❌ Error ditemukan, meminta AI untuk fix...")

        error_context = f"""
                        Command yang dijalankan: `{command}`
                        Output/Error:
                        {result}
                        """
        if context_file:
            file_content = execute_tool("read_file", {"path": context_file})
            error_context += f"""
                            Isi file `{context_file}`:
                            {file_content}
                            """

        error_context += "\nAnalisis error ini dan fix file yang bermasalah, lalu jalankan ulang commandnya."

        messages = [
            {"role": "system", "content": REFLECTION_PROMPT},
            {"role": "user", "content": error_context},
        ]

        # LLM analisis dan fix
        provider.chat_sync(messages, tools=TOOL_DEFINITIONS)

    # Gagal setelah MAX_RETRY
    print(f"\n🚨 Gagal setelah {MAX_RETRY} attempt. Butuh bantuan manual.")
    return {
        "success": False,
        "output": attempts[-1]["output"],
        "attempts": attempts
    }
   