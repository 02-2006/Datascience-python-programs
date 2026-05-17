"""Run LEXGUARD from the project root."""
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix Unicode encode error for emojis on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

if __name__ == "__main__":
    print("\n🛡️  LEXGUARD — Contract Intelligence System")
    print("=" * 45)
    print("  → Open http://localhost:8000 in your browser")
    print("  → Demo: http://localhost:8000/demo")
    print("=" * 45 + "\n")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
