from nice.tools.file_tools import read_file, write_file, list_directory
from nice.tools.shell_tools import run_command

# Definisi tools dalam format yang dimengerti LLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Baca isi file dari disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path ke file yang ingin dibaca"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Tulis content ke file. Buat file baru kalau belum ada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path ke file yang ingin ditulis"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content yang ingin ditulis ke file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lihat isi folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path folder yang ingin dilihat"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Jalankan shell command di terminal dan return outputnya",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command yang ingin dijalankan"
                    }
                },
                "required": ["command"]
            }
        }
    },
]

# Map nama tool ke fungsi Python
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "run_command": run_command,
}

def execute_tool(name: str, arguments: dict) -> str:
    """Jalankan tool berdasarkan nama dan arguments."""
    if name not in TOOL_FUNCTIONS:
        return f"Error: Tool '{name}' tidak ditemukan."
    func = TOOL_FUNCTIONS[name]
    return func(**arguments)
