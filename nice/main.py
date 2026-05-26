import typer

app = typer.Typer(
    name="nice",
    help="Your autonomous CLI AI engineer",
    no_args_is_help=True, #show help when no arguments are provided
)

@app.command()
def ask(prompt: str):
    """Tanya sesuatu ke AI."""
    print(f"kamu bertanya: {prompt}")

@app.command()
def version():
    """Tampilkan versi Nice."""
    print("Nice v0.1.0")

if __name__ == "__main__":
    app()